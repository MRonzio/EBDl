# EBDl encode bed downloader
``` 
usage: ebdl.py [-h] [-o ORGANISM] [-O OUTDIR] [-g GEN] -e EXP_TYPE [-f EXP]
               [-l CL] [-k] [-j] [-t TG] [-p TP] [-s]

EBDl encode bed downloader

optional arguments:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism ORGANISM
                        organism, e.g. Homo+sapiens
  -O OUTDIR, --outdir OUTDIR
                        output folder
  -g GEN, --genome GEN  genome, e.g. hg19, GRCh38, mm10 etc...,default all the
                        ones available
  -e EXP_TYPE, --exp-type EXP_TYPE
                        experiment type: either "TF" or "Histone"
  -f EXP, --factor EXP  target name
  -l CL, --cell-line CL
                        cell line, default all the ones available
  -k, --keep-archived   download also archived analyses (but not archived
                        files)
  -j, --jaspar-download
                        download jaspar matrices(ignored for histones)
  -t TG, --taxonomic-group TG
                        taxonomic group
  -p TP, --threads TP   n threadpool
  -s, --skip-download   skip download, just query, watch the output and get
                        urls




``` 
## packeages needed:
coreapi
wget


# TODO
  - deal with multiple experiments for the same factor in different cell lines/organisms/genome. ---- DONE
  - provide a more meaningful metadata ---- DONE
  - improve speed
  - fix output_dir ---- DONE
  - extend to whole organism (i.e. not only cell lines) experiments. ----- DONE 
