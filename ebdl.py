#!/usr/bin/python3

import json
import os
import requests
import pprint
import argparse
import wget 
from coreapi import Client

headers = {'accept': 'application/json'}
client = Client()
################################################################################
# COMMAND LINE OPTIONS
def cli_options():
    parser = argparse.ArgumentParser(description='EBDl encode bed downloader')
    parser.add_argument('-o', dest='organism', default='Homo+sapiens', help='organism')
    parser.add_argument('-f', dest='tf', default='CTCF', help='transcription factor')
    parser.add_argument('-l', default='K562', dest='cl', help='Cell line')
    parser.add_argument('-g', default='vertebrates', dest='tg', help='taxonomic group')
    return parser.parse_args()


def search_experiments(organism, tf, cl): 
    api_dict = { 'organism': 'replicates.library.biosample.donor.organism.scientific_name','tf': 'target.label','cell_line':'biosample_ontology.term_name'}
    r = requests.get(f"https://www.encodeproject.org/search/?type=Experiment&{api_dict['organism']}={organism}&assay_title=TF+ChIP-seq&status=released&{api_dict['tf']}={tf}&biosample_ontology.classification=cell+line&{api_dict['cell_line']}={cl}",headers=headers)
    rj = r.json()
    if rj['notification'] == "Success":
       return rj
    else: 
       print(rj['notification'] +": FATAL error")
       exit(1)


def bed_files(experiments):
    DownloadUrl_l = [] 
    for x in experiments['@graph']:
        exp = str((x['@id']))
        url = f"https://www.encodeproject.org{exp}"
        exp_r = requests.get(url, headers=headers)
        test = exp_r.json()
        for i,item in enumerate(test['files']):
            if test['files'][i]['output_type']=="optimal IDR thresholded peaks" and test['files'][i]['file_format']=="bed":
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
        
    
if __name__ == '__main__':
    options = cli_options()
    os.mkdir(options.tf)
    experiments = search_experiments(organism=options.organism, tf=options.tf, cl=options.cl)
    results = bed_files(experiments=experiments)
    jaspar = search_jaspar(tf=options.tf,tg=options.tg)
    jaspar_to_file(jaspar,options.tf)
    with open(f'./{options.tf}/bed_files.txt', 'a') as f:
        json.dump(results,f,ensure_ascii=False, indent=4)
    os.chdir(options.tf)
    for i in results:
        wget.download(i['download_url'])
    
