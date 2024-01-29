# flexynesis-benchmarks
Comprehensive continuous benchmarking of tools for multi-omics data integration

# Goal
This repo contains a Snakemake workflow which evaluates the performance of various tools available in ["flexynesis" package](https://github.com/BIMSBbioinfo/flexynesis)
and builds a dashboard that is used to view and compare the performance of different multi-omic integration approaches for various tasks.

# The latest benchmark results can be viewed here:
https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis-benchmark-datasets/dashboard.html

# Usage

## Environment
```
# install dependencies using guix
mkdir $HOME/guix-profiles
guix package --manifest=guix.scm --profile=$HOME/guix-profiles/flexynesis_benchmarks
source $HOME/guix-profiles/flexynesis_benchmarks/etc/profile
```

```
# install flexynesis from source
git clone https://github.com/BIMSBbioinfo/flexynesis.git
cd flexynesis
# create conda env
conda create -n flexenv --file spec-file.txt
conda activate flexenv
# install flexynesis
pip install -e . 

```


## Test run

```
snakemake -p -s flexynesis-benchmarks/Snakefile.py -j 2 --configfile flexynesis-benchmarks/settings_test.yaml 
```

## Full benchmark run
```
snakemake -p -s flexynesis-benchmarks/Snakefile.py -j 2 --configfile flexynesis-benchmarks/settings.yaml 
```


# How to download and process data from cbioportal
The script get_cbioportal_data.R contains a class to download and process cbioportal data.
However, each dataset has its own specific tasks and data cleaning/processing requirements. 
Therefore, I write an additional script for each dataset that runs further processes the data to make it ready for 
analysis by flexynesis. 

## Example: msk_met_2021 dataset 
 This will create three different folders (for various different tasks)
Rscript ./src/prepare_data.msk_met_2021.R ./src/get_cbioportal_data.R

# Overview of datasets used for benchmarking  
An overview of datasets used for benchmarking can be found [here](https://docs.google.com/spreadsheets/d/137D56jlFt_8gM6iJSvaZ6p_Ryx68zC7Nxcd3xhMXAqw/edit?usp=sharing)

 
