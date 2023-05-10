# Download and process msk_met_2021 dataset from Cbioportal, 
# choose relevant tasks; make it ready for analysis by flexynesis for relevant tasks 

# Relevant Tasks 
# 1. Considering all samples 
# What is the difference between any primary sample and any metastatic sample (SAMPLE_TYPE)
# update dat to have the same set of samples in the same order

# 2. considering only primary samples; what is the difference between primary samples of the patients who have no metastasis and those with metastasis?
# - can you predict metastasis burden just looking at primary samples?
# - can you predict the primary site 

args <- commandArgs(trailingOnly = TRUE)

# path to script that contains "CBioPortalData" class.
cbio_download_script = args[1]  #get_cbioportal_data.R


# split into train/test
split_dat <- function(dat, samples = NULL, ratio = 0.7) {
  set.seed(42)
  if(is.null(samples)) {
    samples <- rownames(dat$clin)
  }
  cat(length(samples), "\n")
  train <- sample(samples, round(ratio * length(samples)))
  test <- setdiff(samples, train)
  dat.train <- sapply(simplify = F, names(dat), function(x) {
    if(x == 'clin') {
      dat[[x]][train,]
    } else {
      dat[[x]][,train]
    }
  })
  
  dat.test <- sapply(simplify = F, names(dat), function(x) {
    if(x == 'clin') {
      dat[[x]][test,]
    } else {
      dat[[x]][,test]
    }
  })
  return(list('train' = dat.train, 'test' = dat.test))
} 

# print train/test folders 
print_dataset <- function(dat, outdir) {
  if(!dir.exists(outdir)) {
    dir.create(outdir)
  }
  lapply(names(dat), function(s) {
    p <- file.path(outdir, s)
    if(!dir.exists(p)) {
      dir.create(p)
    }
    lapply(names(dat[[s]]), function(f) {
      write.table(dat[[s]][[f]], 
                  file = file.path(p, paste0(f, ".csv")), sep = ',')
    })
  })
}

source(cbio_download_script)
# Instantiate the CBioPortalData class
cbio <- CBioPortalData$new(study_id = 'ccle_broad_2019') 
# Download and extract a study archive
archive_path <- cbio$download_study_archive() 
study_dir <- cbio$extract_archive(archive_path)
cbio$print_data_files()

# we import gex/cna/mut and drug response data
files <- grep('rpkm.txt|_cna|_mutations|auc.txt|clinical', cbio$data_files, value = T)
dat <- cbio$read_data(files) 
names(dat) <- gsub("data_|.txt", "", names(dat))


# clin data consists of drug response of cell lines and also some additional sample annotations 

clin <- dat$drug_treatment_auc[,-c(2:4)]
clin <- t(data.frame(clin[,-1], row.names = clin[[1]], check.names = F))

dat_all <- list('gex' = dat$mrna_seq_rpkm, 
                'mut' = dat$mutations, 
                'cna' = dat$cna)
# samples that have all data types and available for drug response 
samples <- Reduce(intersect, lapply(dat_all, colnames))
samples <- intersect(rownames(clin), samples)

# find top drugs that are not NA in most samples 
# get top 40 drugs 

drugs <- names(sort(apply(clin[samples,], 2, function(x) sum(is.na(x))), decreasing = T)[1:40])

clin <- clin[samples, drugs]
dat_all$clin <- clin

# split data into training/testing 
dat_all <- split_dat(dat_all, ratio = 0.7)

# print dataset to folder
print_dataset(dat_all, 'ccle_broad_2019_processed')











