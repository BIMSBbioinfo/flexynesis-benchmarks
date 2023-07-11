import os 
import sys
import pandas as pd
import numpy as np

OUTDIR = os.path.abspath(config['outdir'])
SRCDIR = os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), 'src') 
LOGDIR = os.path.join(OUTDIR, 'logs')
RSCRIPT = config['rscript']

feature_perc = config['features_top_percentile']
min_features = config['min_features']
hpo_iterations = config['hpo_iterations']

# get outcome variable dependent on the task 

def get_data_url(task):
    print("getting url for", task)
    url = config['tasks'][task]['url']
    base = os.path.basename(url)
    name = os.path.splitext(base)[0]
    print(url, base, name)
    return url, base, name

def parse_vars(s):
    return {pair.split(':')[0]: pair.split(':')[1] for pair in s.split()}


def get_data_path(task_df, prefix):
    task = task_df[task_df['prefix'] == prefix]['task'].item()
    return os.path.join(OUTDIR, "data", task, ".dummy")
    
def get_model_args(task_df, prefix):
    datapath = os.path.dirname(get_data_path(task_df, prefix))

    batchvar = task_df[task_df['prefix'] == prefix]['batch'].item()
    
    args = " ".join(["--data_path",datapath, 
                     "--model_class",task_df[task_df['prefix'] == prefix]['tool'].item(),
                     "--target_variables",task_df[task_df['prefix'] == prefix]['target'].item(),
                     "--fusion_type",task_df[task_df['prefix'] == prefix]['fusion'].item(),
                     "--hpo_iter",str(task_df[task_df['prefix'] == prefix]['hpo_iter'].item()),
                     "--features_min", str(task_df[task_df['prefix'] == prefix]['features_min'].item()),
                     "--features_top_percentile", str(task_df[task_df['prefix'] == prefix]['feature_perc'].item()),
                     "--data_types", task_df[task_df['prefix'] == prefix]['data_types'].item()])
    
    if batchvar != 'None':
        args = " ".join([args, "--batch_variables", batchvar])
    
    return(args)
    
targets = []
for task in config['tasks'].keys():
    variables = config['tasks'][task]['vars']
    variables = [parse_vars(s) for s in variables]
    tools = config['tasks'][task]['tools'].strip().split(',')
    fusions = config['fusions']
    data_types = config['tasks'][task]['data_types']
    for v in variables:
        for t in tools:
            for f in config['fusions']:
                for d in data_types:
                    targets.append({'task': task, 'target': v['target'], 'batch': v['batch'], 
                                    'tool': t, 'data_types': d, 'fusion': f, 'hpo_iter': hpo_iterations, 
                                    'features_min': min_features, 'feature_perc': feature_perc})

task_df = pd.DataFrame(targets)
task_df['prefix'] = [''.join(['analysis', str(x)]) for x in task_df.index]

TASKS=list(np.unique(task_df['task']))
ANALYSES=list(task_df['prefix'])

rule all:
    input:
        # print analysis table
        os.path.join(OUTDIR, "analysis_table.csv"),
        # input data download
        expand(os.path.join(OUTDIR, "data", "{task}", ".dummy"), task = TASKS),
        # modeling results
        expand(os.path.join(OUTDIR, "results", "{analysis}.{output_type}.csv"), 
               analysis = ANALYSES, 
               output_type = ['stats', 'feature_importance', 'embeddings_train', 'embeddings_test']),
        # dashboard
        os.path.join(OUTDIR, "dashboard.html")

rule print_analysis_table:
    output:
        os.path.join(OUTDIR, "analysis_table.csv")
    run:
        task_df.to_csv(output[0])
        
rule download_data:
    output:
        os.path.join(OUTDIR, "data", "{task}", ".dummy") 
    log: 
        os.path.join(LOGDIR, "download.{task}.log")
    params: 
        url = lambda wildcards: get_data_url(wildcards.task)[0],
        # download to task folder
        downloaded_tgz = lambda wildcards: os.path.join(OUTDIR, "data", get_data_url(wildcards.task)[1]),
        # extract the folder 
        extracted =  lambda wildcards: get_data_url(wildcards.task)[2],
        # name folder to "task" name
        new_name = lambda wildcards: os.path.join(OUTDIR, "data", wildcards.task),
    shell:
        """
        curl -L -o {params.downloaded_tgz} {params.url} 
        tar -xzvf {params.downloaded_tgz}
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
        os.path.join(OUTDIR, "results", "{analysis}.embeddings_test.csv")
    log: 
        os.path.join(LOGDIR, "{analysis}.log")
    params: 
        args = lambda wildcards: get_model_args(task_df, wildcards.analysis),
        outdir = os.path.join(OUTDIR, "results")
    shell:
        """
        flexynesis {params.args} --outdir {params.outdir} --prefix {wildcards.analysis} > {log} 2>&1
        """

        
rule dashboard:
    input:
        expand(os.path.join(OUTDIR, "results", "{analysis}.{output_type}.csv"), 
               analysis = ANALYSES, 
               output_type = ['stats', 'feature_importance', 'embeddings_train', 'embeddings_test'])
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
