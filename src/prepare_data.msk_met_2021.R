
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
cbio <- CBioPortalData$new(study_id = 'msk_met_2021') 
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

# prepare main data
clin <- subset(dat$clinical_sample, select = c('SAMPLE_ID', 'ORGAN_SYSTEM', 'SUBTYPE', 'SUBTYPE_ABBREVIATION', 
                                               'SAMPLE_TYPE', 'PRIMARY_SITE', 'METASTATIC_SITE', 'MET_COUNT', 'MET_SITE_COUNT', 
                                               'CANCER_TYPE', 'FGA', 'MSI_SCORE', 'TMB_NONSYNONYMOUS'))
clin <- data.frame(clin[,-1], row.names = clin[[1]], check.names = F)
samples <- intersect(dat$clinical_sample$SAMPLE_ID, intersect(colnames(dat$cna), colnames(dat$mutations)))
clin <- clin[samples, ]

dat <- list('cna' = dat$cna[,samples], 
            'mut' = dat$mutations[,samples],
            'clin' = clin[samples,])

# split all data into train test
dat_all <- split_dat(dat)

# subset for primary samples and then split for train/test 
primary_samples <- rownames(clin[clin$SAMPLE_TYPE == 'Primary',])
dat_primary <- split_dat(dat, primary_samples)

# subset for metastatic samples and then split for train/test
metastatic_samples <- rownames(clin[clin$SAMPLE_TYPE == 'Metastasis',])
dat_metastasis <- split_dat(dat, metastatic_samples)

print_dataset(dat_all, 'msk_met_2021_all')
print_dataset(dat_primary, 'msk_met_2021_primary')
print_dataset(dat_metastasis, 'msk_met_2021_metastasis')

cat(date(), " => finished printing msk_met_2021 datasets")

