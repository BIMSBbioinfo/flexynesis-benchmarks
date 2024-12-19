# Goal

This repo contains a Snakemake workflow which evaluates the performance of various tools available in ["flexynesis" package](https://github.com/BIMSBbioinfo/flexynesis)
and builds a dashboard that is used to view and compare the performance of different multi-omic integration approaches for various tasks.

The latest benchmark results can be viewed here: https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis-benchmark-datasets/dashboard.html

# Usage

## Environment

Create an environment including snakemake, flexynesis, and all other necessary dependencies. 


```
git clone https://github.com/BIMSBbioinfo/flexynesis-benchmarks.git
cd flexynesis-benchmarks 
mamba create -n flex_benchmarks_env python==3.11 snakemake
mamba activate flex_benchmarks_env
pip install flexynesis 
# install slurm or SGE plugins for cluster submission
mamba install snakemake-executor-plugin-slurm  <=OR=> mamba install snakemake-executor-plugin-cluster-generic
```


## Test run

```
mamba activate flex_benchmarks_env
snakemake -p -s Snakefile.py -j 2 --configfile settings_test.yaml --profile ./slurm

OR 

snakemake -p -s Snakefile.py -j 2 --configfile settings_test.yaml --profile ./sge 
 
```

## Full benchmark run
```
mamba activate flex_benchmarks_env
snakemake -p -s Snakefile.py -j 2 --configfile settings.yaml 
```



 
