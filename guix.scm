(use-modules (gnu)
             (guix profiles)
             (guix packages)
             (guix utils)
             (guix download)
             (guix build-system gnu)
             (guix licenses)
             ;; Import modules for Python and R packages
             (gnu packages python)
             (gnu packages bioinformatics)
             (gnu packages statistics)
)

;; Define the list of packages
(define my-packages
  (list
    (specification->package "conda")
    ;; Python packages - replace with actual Guix package names
    (specification->package "python")
    (specification->package "python-pyyaml")
    (specification->package "python-pandas")
    ;; Bioinformatics tools
    (specification->package "snakemake")
    ;; R packages - ensure these are the correct names in Guix
    (specification->package "r")
    (specification->package "r-data-table")
    (specification->package "r-yaml")
    (specification->package "r-ggplot2")
    (specification->package "r-knitr")
    (specification->package "r-ggrepel")
    (specification->package "r-pbapply")
    (specification->package "r-biostrings")
    (specification->package "r-rmarkdown")
    (specification->package "r-ggpubr")
    (specification->package "r-pheatmap")
    ;; Additional packages as needed
    ))

;; Convert the list of packages to a manifest
(packages->manifest my-packages)

