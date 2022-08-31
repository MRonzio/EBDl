#!/usr/bin/env python3
from ArgParser import dloptions
import json
import os
import requests
import wget
from coreapi import Client
from multiprocessing.pool import ThreadPool

headers = {'accept': 'application/json'}
client = Client()
################################################################################

def search_experiments(organism, exp_type, exp, cl, genome): 
    api_dict = {'organism': 'replicates.library.biosample.donor.organism.scientific_name',
                'assay' : 'assay_title',
                'exp': 'target.label',
                'cell_line':'biosample_ontology.term_name',
                'genome':'assembly'
                }

    r = (f"https://www.encodeproject.org/search/?type=Experiment"\
        f"&{api_dict['organism']}={organism}"\
        f"&{api_dict['assay']}={exp_type}&status=released"\
        f"&{api_dict['exp']}={exp}"\
        f"&{api_dict['genome']}={genome}"\
        "&biosample_ontology.classification=cell+line"\
        "&perturbed=false"\
        "&limit=all"\
        f"&{api_dict['cell_line']}={cl}")

    rs=requests.get(r,headers=headers)
    rj = rs.json()
    print(r)
    if rj['notification'] == "Success":
       return rj
    else: 
       print(rj['notification'] +": FATAL error")
       exit(1)


def DisplayENCODEquery(set_options):
    print(f"Organism : {set_options.organism}")
    print(f"Cell Line : {set_options.cl}")
    print(f"Genome : {set_options.gen}")
    print(f"Exp Type : {set_options.exp_type}")
    print(f"Exp : {set_options.exp}")


def bed_files(experiments,genome):
    DownloadUrl_l = [] 
    for x in experiments['@graph']:
        expr = str((x['@id']))
        url = f"https://www.encodeproject.org{expr}"
        expr_r = requests.get(url, headers=headers)
        test = expr_r.json()
        for i,item in enumerate(test['files']):
            try:
                test['files'][i]['preferred_default']=="True"
                #print(f"this is default! for {test['files'][i]}")
            except KeyError:
                #print(f"no default available for {test['files'][i]}")
                continue
            if (test['files'][i]['output_type']=="optimal IDR thresholded peaks"\
            or test['files'][i]['output_type']=="IDR thresholded peaks"\
            or test['files'][i]['output_type']=="pseudoreplicated peaks")\
            and test['files'][i]['file_format']=="bed"\
            and test['files'][i]['assembly']==genome:

                dl = item['href']
                accession = item['accession']
                #name = item['']
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
    options = dloptions()
    jd_opt=bool(options.jd)
    DisplayENCODEquery(set_options=options)
    exp_type_opt=options.exp_type + '+ChIP-seq'
    experiments = search_experiments(organism=options.organism,
                                     exp_type=exp_type_opt,
                                     exp=options.exp,
                                     cl=options.cl,
                                     genome=options.gen)  
    results = bed_files(experiments=experiments,genome=options.gen)
    if options.exp=='*':
        exp_opt="all"
    else:
        exp_opt=options.exp
    createdir(exp_opt)
    if jd_opt==True and exp_type_opt == 'TF+ChIP-seq' and exp_opt!="all" :
        jaspar = search_jaspar(tf=options.exp,tg=options.tg)
        jaspar_to_file(jaspar,options.exp)
    with open(f'./{exp_opt}/bed_files.txt', 'a') as f:
        json.dump(results,f,ensure_ascii=False, indent=4)
    os.chdir(exp_opt)
    urls=[]
    for i in results:
        urls.append(i['download_url'])
    p = ThreadPool(int(options.tp)) 
    p.map(download,urls)
