# Download and process brca_metabric dataset from Cbioportal, 
# choose relevant tasks; make it ready for analysis by flexynesis for relevant tasks 

# Relevant Tasks 
# survival modeling, subtype prediction

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
cbio <- CBioPortalData$new(study_id = 'brca_metabric') 
# Download and extract a study archive
archive_path <- cbio$download_study_archive() 
study_dir <- cbio$extract_archive(archive_path)
cbio$print_data_files()

# we import gex/cna/mut and drug response data
files <- grep('illumina_microarray.txt|_cna|_mutations|clinical', cbio$data_files, value = T)
dat <- cbio$read_data(files) 
names(dat) <- gsub("data_|.txt", "", names(dat))


clin <- dat$clinical_patient
clin <- data.frame(clin[,-1], row.names = clin[[1]], check.names = F)
# convert COHORT info to character
clin$COHORT <- paste0('cohort', clin$COHORT)

dat_all <- list('gex' = dat$mrna_illumina_microarray, 
                'mut' = dat$mutations, 
                'cna' = dat$cna)
# samples that have all data types 
samples <- Reduce(intersect, lapply(dat_all, colnames))
samples <- intersect(rownames(clin), samples)

clin <- clin[samples, ]
dat_all$clin <- clin

# split data into training/testing 
dat_all <- split_dat(dat_all, ratio = 0.7)

# print dataset to folder
print_dataset(dat_all, 'brca_metabric_processed')











