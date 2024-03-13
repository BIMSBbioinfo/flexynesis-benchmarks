import os 
import sys
import pandas as pd
import numpy as np
from itertools import product

OUTDIR = os.path.abspath(config['outdir'])
SRCDIR = os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), 'src') 
LOGDIR = os.path.join(OUTDIR, 'logs')
RSCRIPT = config['rscript']

def get_data_url(task_df, prefix):
    task = task_df[task_df['prefix'] == prefix]['task'].item()
    url = config['tasks'][task]['url']
    base = os.path.basename(url)
    name = os.path.splitext(base)[0]
    #print("url for prefix", prefix, "task:",task)
    return url, base, name, task

def get_data_path(task_df, prefix):
    task = task_df[task_df['prefix'] == prefix]['task'].item()
    return os.path.join(OUTDIR, "data", prefix, ".dummy")

def parse_vars(s):
    # Improved with handling for spaces within the values
    return dict(pair.split(':') for pair in s.split())

def parse_tool(tool_string):
    """
    Parses a tool string to identify the tool and its optional convolution type.
    Returns the tool and conv_type (None if not specified).
    """
    parts = tool_string.split(':', 1)
    return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], None)

def get_combinations(task_settings):
    # Unpack settings
    variables = [parse_vars(s) for s in task_settings['vars']]
    tools = task_settings['tools'].strip().split(',')
    data_types = task_settings['data_types']
    fusions = task_settings['fusions']
    loss_weighting = ['True', 'False'] # try both setting

    # single switches 
    min_features = task_settings['min_features']
    hpo_iterations = task_settings['hpo_iterations']
    early_stop_patience = task_settings['early_stop_patience']
    log_transform = task_settings['log_transform']
    features_top_percentile = task_settings['features_top_percentile']

    # Generate all combinations
    combinations = product(variables, tools, fusions, data_types, loss_weighting)
    
    combs = []
    for variables, tool, fusion, data_type, loss_weighting in combinations:
        tool, gnn_conv = parse_tool(tool)
        arguments = {
            'task': task,
            'tool': tool,
            'gnn_conv': gnn_conv, #optional
            'target': variables.get('target', None),
            'batch': variables.get('batch', None),  
            'event': variables.get('event', None),
            'time': variables.get('time', None),
            'data_types': data_type,
            'fusion': fusion,
            'hpo_iter': hpo_iterations,
            'early_stop_patience': early_stop_patience,
            'features_min': min_features,
            'feature_perc': features_top_percentile,
            'log_transform': log_transform,
            'use_loss_weighting': loss_weighting
        }        
        combs.append(arguments)
    return combs

def get_model_args(task_df, prefix):
    # Retrieve the row for the given prefix to minimize repetitive indexing
    task_row = task_df[task_df['prefix'] == prefix].iloc[0]
    
    datapath = os.path.dirname(get_data_path(task_df, prefix))
    
    args = ["flexynesis --use_gpu"]
    
    args.extend([
        "--data_path", datapath,
        "--model_class", task_row['tool'],
        "--fusion_type", task_row['fusion'],
        "--hpo_iter", str(task_row['hpo_iter']),
        "--early_stop_patience", str(task_row['early_stop_patience']),
        "--features_min", str(task_row['features_min']),
        "--features_top_percentile", str(task_row['feature_perc']),
        "--use_loss_weighting", task_row['use_loss_weighting'],
        "--data_types", task_row['data_types'],
        "--log_transform", str(task_row['log_transform'])
    ])
    
    if task_row['target']:
        args.extend(["--target_variables", task_row['target']])
    if task_row['batch']:
        args.extend(["--batch_variables", task_row['batch']])
    if task_row['event']:
        args.extend(["--surv_event_var", task_row['event']])
    if task_row['time']:
        args.extend(["--surv_time_var", task_row['time']])
    if task_row['gnn_conv']:
        args.extend(["--gnn_conv_type", task_row['gnn_conv']])
    # Join the arguments into a command-line friendly string
    command_line_args = " ".join(args)
    
    return command_line_args


targets = []
for task, settings in config['tasks'].items():
    targets.extend(get_combinations(settings))

task_df = pd.DataFrame(targets)
task_df['prefix'] = ['analysis' + str(x) for x in task_df.index]

print(task_df)

TASKS=list(np.unique(task_df['task']))
ANALYSES=list(task_df['prefix'])

rule all:
    input:
        # print analysis table
        os.path.join(OUTDIR, "analysis_table.csv"),
        # input data download
        expand(os.path.join(OUTDIR, "data", "{analysis}", ".dummy"), analysis = ANALYSES),
        # modeling results
        expand(os.path.join(OUTDIR, "results", "{analysis}.{output_type}.csv"), 
               analysis = ANALYSES, 
               output_type = ['stats', 'feature_importance', 'embeddings_train', 'embeddings_test', 
                             'embeddings_train.filtered', 'embeddings_test.filtered']),
        # dashboard
        os.path.join(OUTDIR, "dashboard.html")

rule print_analysis_table:
    output:
        os.path.join(OUTDIR, "analysis_table.csv")
    run:
        task_df.to_csv(output[0])
        
rule download_data:
    output:
        os.path.join(OUTDIR, "data", "{analysis}", ".dummy") 
    log: 
        os.path.join(LOGDIR, "download.{analysis}.log")
    params: 
        url = lambda wildcards: get_data_url(task_df, wildcards.analysis)[0],
        # download to task folder
        downloaded_tgz = lambda wildcards: os.path.join(OUTDIR, "data", wildcards.analysis, get_data_url(task_df, wildcards.analysis)[1]),
        # extract the folder 
        extracted =  lambda wildcards: os.path.join(OUTDIR, "data", wildcards.analysis, get_data_url(task_df, wildcards.analysis)[2]),
        # name folder to "task" name
        new_name = lambda wildcards: os.path.join(OUTDIR, "data", wildcards.analysis)
    shell:
        """
        curl -L -o {params.downloaded_tgz} {params.url} 
        tar -xzvf {params.downloaded_tgz} -C {params.new_name}
        mv {params.extracted}/* {params.new_name}; rm -rf {params.extracted}
        touch {output} 
        """
        
rule model:
    input:
        lambda wildcards: get_data_path(task_df, wildcards.analysis)
    output: 
        os.path.join(OUTDIR, "results", "{analysis}.stats.csv"),
        os.path.join(OUTDIR, "results", "{analysis}.feature_importance.csv"),
        os.path.join(OUTDIR, "results", "{analysis}.embeddings_train.csv"),
        os.path.join(OUTDIR, "results", "{analysis}.embeddings_test.csv"),
        os.path.join(OUTDIR, "results", "{analysis}.embeddings_train.filtered.csv"),
        os.path.join(OUTDIR, "results", "{analysis}.embeddings_test.filtered.csv")

    log: 
        os.path.join(LOGDIR, "{analysis}.log")
    params: 
        args = lambda wildcards: get_model_args(task_df, wildcards.analysis),
        outdir = os.path.join(OUTDIR, "results")
    shell:
        """
        {params.args} --outdir {params.outdir} --prefix {wildcards.analysis} > {log} 2>&1
        """

        
rule dashboard:
    input:
        expand(os.path.join(OUTDIR, "results", "{analysis}.{output_type}.csv"), 
               analysis = ANALYSES, 
               output_type = ['stats', 'feature_importance', 'embeddings_train', 'embeddings_test', 
                             'embeddings_train.filtered', 'embeddings_test.filtered'])
    output: 
        os.path.join(OUTDIR, "dashboard.html")
    log: 
        os.path.join(LOGDIR, "dashboard.log")
    params:
        render_script = os.path.join(SRCDIR, "render_dashboard.R"),
        rmd_file = os.path.join(SRCDIR, "dashboard.Rmd"),
    shell:
        """
        {RSCRIPT} {params.render_script} {params.rmd_file} {output} {OUTDIR} > {log} 2>&1
        """
