# EBDl encode bed downloader
``` 

optional arguments:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism ORGANISM
                        organism, e.g. Homo+sapiens
  -O OUTDIR, --outdir OUTDIR
                        output folder
  -g GEN, --genome GEN  genome, e.g. hg19, GRCh38, mm10 etc...
  -e EXP_TYPE, --exp-type EXP_TYPE
                        experiment type: either "TF" or "Histone"
  -f EXP, --factor EXP  target name
  -l CL, --cell-line CL
                        cell line
  -j, --jaspar-download
                        download jaspar matrices(ignored for histones)
  -t TG, --taxonomic-group TG
                        taxonomic group
  -p TP, --threads TP   n threadpool




``` 
## packeages needed:
coreapi


# TODO
  - deal with multiple experiments for the same factor in different cell lines/organisms/genome.
  - 