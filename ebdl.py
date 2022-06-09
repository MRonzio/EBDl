#!/usr/bin/env python3

import json
import os
import requests
import argparse
import wget 
from coreapi import Client
from multiprocessing.pool import ThreadPool

headers = {'accept': 'application/json'}
client = Client()
################################################################################
# COMMAND LINE OPTIONS
def cli_options():
    parser = argparse.ArgumentParser(description='EBDl encode bed downloader')
    parser.add_argument('-o', '--organism', dest='organism', default='Homo+sapiens', help='organism')
    parser.add_argument('-g', '--genome', dest='gen', default='*', help='genome such as hg19, GRCh38, mm10 etc...')
    parser.add_argument('-e', '--exp-type', dest='exp_type', default='TF', help='experiment type: either "TF" or "Histone"')
    parser.add_argument('-f', '--factor', dest='exp', default='CTCF', help='target name')
    parser.add_argument('-l', '--cell-line',default='K562', dest='cl', help='cell line')
    parser.add_argument('-j', '--jaspar-download', default=False, dest='jd', action='store_true',
                         help='boolean download jaspar (only for tfs)')
    parser.add_argument('-t', '--taxonomic-group', default='vertebrates', dest='tg', help='taxonomic group')
    parser.add_argument('-p', '--threads', default=4 , dest='tp' , help='n threadpool')
    return parser.parse_args()


def search_experiments(organism, exp_type, exp, cl, genome): 
    api_dict = {'organism': 'replicates.library.biosample.donor.organism.scientific_name',
                'assay' : 'assay_title',
                'exp': 'target.label',
                'cell_line':'biosample_ontology.term_name',
                'genome':'assembly'
                }

    r = requests.get(f"https://www.encodeproject.org/search/?type=Experiment"\
        f"&{api_dict['organism']}={organism}"\
        f"&{api_dict['assay']}={exp_type}&status=released"\
        f"&{api_dict['exp']}={exp}"\
        "&biosample_ontology.classification=cell+line"\
        "&perturbed=false"\
        f"&{api_dict['genome']}={genome}"\
        f"&{api_dict['cell_line']}={cl}",headers=headers)

    rj = r.json()
    if rj['notification'] == "Success":
       return rj
    else: 
       print(rj['notification'] +": FATAL error")
       exit(1)


def bed_files(experiments):
    DownloadUrl_l = [] 
    for x in experiments['@graph']:
        expr = str((x['@id']))
        url = f"https://www.encodeproject.org{expr}"
        expr_r = requests.get(url, headers=headers)
        test = expr_r.json()
        for i,item in enumerate(test['files']):

            if (test['files'][i]['output_type']=="optimal IDR thresholded peaks"\
            or test['files'][i]['output_type']=="IDR thresholded peaks"\
            or test['files'][i]['output_type']=="pseudoreplicated peaks")\
            and test['files'][i]['file_format']=="bed":

               dl = item['href']
               accession = item['accession']
               download_url = f'https://www.encodeproject.org{dl}'
               url_info =  f'https://www.encodeproject.org/files/{accession}'
               bed_file = {'url_info': url_info, 'download_url': download_url }
               DownloadUrl_l.append(bed_file)
    return DownloadUrl_l

def search_jaspar(tf,tg):
    r = client.get(f"https://jaspar.genereg.net/api/v1/matrix/?name={tf}&format=jaspar&tax_group={tg}")
    pwms = r.split('>')[1:]
    return(pwms)


def jaspar_to_file(jaspar,dir):
    #TODO aggiungi char iniziale
    for n,i in enumerate(jaspar):
        matrix_id = i.split()[0]
        f = open(f'./{dir}/{matrix_id}.jaspar', 'a')
        f.write(f'>{jaspar[n]}')
        f.close()

        
def download(url):
    wget.download(url)

def createdir(exp_name):
    if os.path.exists(exp_name):
        print(f'{exp_name} already present, skipping it...')
        exit(1)
    else:
        os.mkdir(exp_name)

if __name__ == '__main__':
    options = cli_options()
    exp_type_opt=options.exp_type + '+ChIP-seq'
    experiments = search_experiments(organism=options.organism,
                                     exp_type=exp_type_opt,
                                     exp=options.exp,
                                     cl=options.cl,
                                     genome=options.gen)
    createdir(options.exp)
    results = bed_files(experiments=experiments)
    if options.exp_type=='TF' and options.jd==True:
        jaspar = search_jaspar(tf=options.exp,tg=options.tg)
        jaspar_to_file(jaspar,options.exp)
    with open(f'./{options.exp}/bed_files.txt', 'a') as f:
        json.dump(results,f,ensure_ascii=False, indent=4)
    os.chdir(options.exp)
    urls=[]
    for i in results:
        urls.append(i['download_url'])
    p = ThreadPool(int(options.tp)) 
    p.map(download,urls)
