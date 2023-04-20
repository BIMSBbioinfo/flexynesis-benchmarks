import os 
import sys

OUTDIR = os.path.abspath(config['outdir'])
SRCDIR = os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), 'src') 
LOGDIR = os.path.join(OUTDIR, 'logs')
RSCRIPT = config['rscript']

feature_perc = config['features_top_percentile']
min_features = config['min_features']
hpo_iterations = config['hpo_iterations']

# get outcome variable dependent on the task 
def get_y(task):
    return config['tasks'][task]['y'].split(',')

def get_tools(task):
    modeling_type = config['tasks'][task]['type']
    tools = config['tools'][modeling_type]
    return tools

def get_task_type(task):
    return config['tasks'][task]['type']

def get_data_types(task):
    return config['tasks'][task]['data_types']

def get_data_url(task):
    print("getting url for", task)
    url = config['tasks'][task]['url']
    base = os.path.basename(url)
    name = os.path.splitext(base)[0]
    print(url, base, name)
    return url, base, name


targets = []
for task in config['tasks'].keys():
    ys = get_y(task)
    tools = get_tools(task)
    for y in ys:
        for t in tools:
            for f in config['fusions']:
                target = os.path.join(OUTDIR, task, '.'.join([t, f, y, 'csv']))
                targets.append(target)
            
rule all:
    input:
        # input data download
        expand(os.path.join(OUTDIR, "data", "{task}", ".dummy"), task = config['tasks'].keys()),
        # modeling results
        targets,
        # dashboard
        os.path.join(OUTDIR, "dashboard.html")

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
        os.path.join(OUTDIR, "data", "{task}", ".dummy") 
    output: 
        os.path.join(OUTDIR, "{task}", "{model}.{fusion}.{y}.csv") 
    log: 
        os.path.join(LOGDIR, "{task}.{model}.{fusion}.{y}.log")
    params: 
        data_path = lambda wildcards: os.path.join(OUTDIR, "data", wildcards.task),
        data_types = lambda wildcards: get_data_types(wildcards.task),
        task_type = lambda wildcards: get_task_type(wildcards.task)
    shell:
        """
        flexynesis --data_path {params.data_path} --model_class {wildcards.model} --outcome_var {wildcards.y} --task {params.task_type} --fusion_type {wildcards.fusion} --hpo_iter {hpo_iterations} --features_min {min_features} --features_top_percentile {feature_perc} --data_types {params.data_types} --outfile {output} > {log} 2>&1
        """
        
rule dashboard:
    input:
        targets
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
