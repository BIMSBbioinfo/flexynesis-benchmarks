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
conda env create -f environment.yaml
```


## Test run

```
conda activate flex_benchmark_env
snakemake -p -s Snakefile.py -j 2 --configfile settings_test.yaml 
```

## Full benchmark run
```
conda activate flex_benchmark_env
snakemake -p -s Snakefile.py -j 2 --configfile settings.yaml 
```



 
