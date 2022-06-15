#!/usr/bin/env python3
import argparse

# COMMAND LINE OPTIONS
def dloptions():
    parser = argparse.ArgumentParser(description='EBDl encode bed downloader')
    parser.add_argument('-o', '--organism', dest='organism', default='Homo+sapiens', help='organism')
    parser.add_argument('-O', '--outdir', dest='outdir', help='output folder')
    parser.add_argument('-g', '--genome', dest='gen', default='*', help='genome such as hg19, GRCh38, mm10 etc...')
    parser.add_argument('-e', '--exp-type', dest='exp_type', default='TF', help='experiment type: either "TF" or "Histone"')
    parser.add_argument('-f', '--factor', dest='exp', default='*', help='target name')
    parser.add_argument('-l', '--cell-line',default='*', dest='cl', help='cell line')
    parser.add_argument('-j', '--jaspar-download', default=True, dest='jd', action='store_true',
                        help='boolean download jaspar (ignored for histones)')
    parser.add_argument('-t', '--taxonomic-group', default='vertebrates', dest='tg', help='taxonomic group')
    parser.add_argument('-p', '--threads', default=4 , dest='tp' , help='n threadpool')
    return parser.parse_args()
