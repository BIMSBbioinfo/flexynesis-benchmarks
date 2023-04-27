# flexynesis-benchmarks
Comprehensive continuous benchmarking of tools for multi-omics data integration

# Goal
This repo contains a Snakemake workflow which evaluates the performance of various tools available in ["flexynesis" package](https://github.com/BIMSBbioinfo/flexynesis)
and builds a dashboard that is used to view and compare the performance of different multi-omic integration approaches for various tasks.

# The latest benchmark results can be viewed here:
https://bimsbstatic.mdc-berlin.de/akalin/buyar/flexynesis-benchmark-datasets/dashboard.html


# How to download and process data from cbioportal
The script get_cbioportal_data.R contains a class to download and process cbioportal data.
However, each dataset has its own specific tasks and data cleaning/processing requirements. 
Therefore, I write an additional script for each dataset that runs further processes the data to make it ready for 
analysis by flexynesis. 

## Example: msk_met_2021 dataset 
 This will create three different folders (for various different tasks)
Rscript ./src/prepare_data.msk_met_2021.R ./src/get_cbioportal_data.R



 
