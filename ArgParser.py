#!/usr/bin/env python3
import argparse

# COMMAND LINE OPTIONS
def dloptions():
    parser = argparse.ArgumentParser(description='EBDl encode bed downloader')
    parser.add_argument('-o', '--organism', dest='organism', default='Homo+sapiens', help='organism, e.g. Homo+sapiens')
    parser.add_argument('-O', '--outdir', dest='outdir', help='output folder')
    parser.add_argument('-g', '--genome', dest='gen', default='*', help='genome, e.g. hg19, GRCh38, mm10 etc...,'
                       'default all the ones available')
    parser.add_argument('-e', '--exp-type', dest='assay', required=True, help='experiment type: either "TF" or "Histone"')
    parser.add_argument('-f', '--factor', dest='exp', default='*', help='target name')
    parser.add_argument('-l', '--cell-line',default='*', dest='cl', help='cell line, default all the ones available')
    parser.add_argument('-k', '--keep-archived', dest='ka', action='store_true',
                        help='download also archived analyses (but not archived files)')
    parser.add_argument('-j', '--jaspar-download', dest='jd', action='store_true',
                        help='download jaspar matrices(ignored for histones)')
    parser.add_argument('-c', '--beyond-cell-lines', dest='beyond_cell_line', action='store_true',
                        help='include primary cells, whole organisms etc.')                        
    parser.add_argument('-t', '--taxonomic-group', default='vertebrates', dest='tg', help='taxonomic group')
    parser.add_argument('-p', '--threads', default=4 , dest='tp' , help='n threadpool')
    parser.add_argument('-s', '--skip-download', dest='sd', action='store_true',
                        help='skip download, just query, watch the output and get urls')
    return parser.parse_args()
