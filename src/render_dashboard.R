# render_report.R
args <- commandArgs(trailingOnly = TRUE)
rmd_file <- args[1]
output_file <- args[2]
workdir <- args[3]
rmarkdown::render(input = rmd_file,
                  output_file = output_file, 
                  intermediates_dir = workdir, 
                  output_dir = workdir,
                  params = list(workdir = workdir))
cat(date(), " => finished rendering the dashboard.html")
