
# Download and process Ovarian Serous Cystadenocarcinoma (osc_tcga_2016) dataset from Cbioportal,
# choose relevant tasks; make it ready for analysis by flexynesis for relevant tasks 

# Relevant Tasks 
# TBD

args <- commandArgs(trailingOnly = TRUE)

# path to script that contains "CBioPortalData" class.
cbio_download_script <- args[1]  #get_cbioportal_data.R

# split into train/test
split_dat <- function(dat, samples = NULL) {
  set.seed(42)
  if(is.null(samples)) {
    samples <- rownames(dat$clin)
  }
  cat(length(samples), "\n")
  train <- sample(samples, round(0.5 * length(samples)))
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
cbio <- CBioPortalData$new(study_id = 'ov_tcga')
# Download and extract a study archive
archive_path <- cbio$download_study_archive() 
study_dir <- cbio$extract_archive(archive_path)
cbio$print_data_files()
files <- grep('_mrna|_clinical|_cna|_mutations', cbio$data_files, value = T)
dat <- cbio$read_data(files) 
names(dat) <- gsub("data_|.txt", "", names(dat))

# now to custom data processing for this dataset; 
# for this dataset there is a 1-to-1 mapping of patients and samples, so, I will use sample ids as the common denominator
# relevant tasks are metastasis burden; sample type (primary vs metastatic); 
# there are patients with metastasis and without any metastasis; we can infer for some patients (based on MET_COUNT) if they have any metastasis or not. 
# for both primary/metastatic samples; every patient is sequenced only once 
