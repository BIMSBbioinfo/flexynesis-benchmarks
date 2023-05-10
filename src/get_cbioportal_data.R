# download and process data matrices and annotations from Cbioportal
library(httr)
library(utils)
library(readr)

CBioPortalData <- R6::R6Class("CBioPortalData",
                              public = list(
                                base_url = "https://cbioportal-datahub.s3.amazonaws.com",
                                study_id = NULL,
                                data_files = NULL,
                                initialize = function(base_url = NULL, study_id = NULL, data_files = NULL) {
                                  if (!is.null(base_url)) {
                                    self$base_url <- base_url
                                  }
                                  if(!is.null(study_id)) {
                                    self$study_id <- study_id
                                  }
                                  self$data_files = data_files
                                },
                                download_study_archive = function() {
                                  url <- file.path(self$base_url, paste0(self$study_id, ".tar.gz"))
                                  dest_file <- paste0(self$study_id, ".tar.gz")
                                  if(!file.exists(dest_file)) {
                                    download.file(url, dest_file, mode = "wb")
                                  }
                                  return(dest_file)
                                },
                                
                                extract_archive = function(archive_path) {
                                  base = strsplit(archive_path, "\\.")[[1]][1]
                                  if(!dir.exists(base)) {
                                    untar(archive_path) 
                                  }
                                  self$data_files = dir(base, "^data_.*.txt")
                                  return(base)
                                }, 
                                
                                read_data = function(files = NULL) {
                                  if(is.null(files)) {
                                   files <- self$data_files 
                                  }
                                  cat("Will import data files",files,"\n")
                                  sapply(simplify = F, files, function(x) {
                                    cat(date(), "=> importing",file.path(self$study_id, x),"\n")
                                    dt <- data.table::fread(cmd = paste0("grep -v ^# ",file.path(self$study_id, x))) 
                                    if(grepl('mutations', x)) {
                                      cat("binarizing and converting to matrix", x, "\n")
                                      dt <- self$binarize_mutations(dt)
                                    } else if (!grepl('clinical|drug_treatment', x)) {
                                      cat("converting ",x," to matrix\n")
                                      dt <- self$process_dat(dt)
                                    } 
                                    return(dt)
                                  })
                                },
                                process_dat = function(dt) {
                                  # exclude EntrezGeneID field 
                                  cols <- setdiff(colnames(dt), c('Hugo_Symbol', 'Entrez_Gene_Id'))
                                  # remove non-unique rows 
                                  dt <- dt[!Hugo_Symbol %in% names(which(table(dt[['Hugo_Symbol']]) > 1))]
                                  M <- as.matrix(data.frame(subset(dt, select = cols), row.names = dt[['Hugo_Symbol']], check.names = F))
                                  return(M)
                                },
                                binarize_mutations = function(dt) {
                                  # convert mutation data to binary matrix of genes vs samples 
                                  lapply(c("Hugo_Symbol", "Tumor_Sample_Barcode"), function(f) {
                                    if(!f %in% colnames(dt)){
                                      cat(colnames(dt),"\n")
                                      stop("Can't map mutations to sample ids.", f," not found")
                                    }
                                  })
                                  dt <- dt[,length(Variant_Classification), by = c('Hugo_Symbol', 'Tumor_Sample_Barcode')]
                                  dtc <- data.table::dcast.data.table(dt, Hugo_Symbol ~ Tumor_Sample_Barcode, value.var = 'V1')
                                  dtc <- self$process_dat(dtc) 
                                  dtc[is.na(dtc)] <- 0
                                  dtc[dtc > 0] <- 1
                                  return(dtc)
                                },
                                print_data_files = function() {
                                  print(knitr::kable(self$data_files))
                                }
                              )
)






