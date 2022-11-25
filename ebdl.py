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

def search_experiments(options): 
    api_dict ={}
    for key in vars(options):
        match key:
            case "organism":
                if options.organism is not None:
                    api_dict["replicates.library.biosample.donor.organism.scientific_name"]=options.organism
            case "assay":
                if options.assay in ['TF','Histone'] :
                    api_dict["assay_title"]= f"{options.assay} ChIP-seq"
                else:
                    print(f"TF or Histone assay available. You put {options.assay}, exiting..")
                    exit(1)
            case "trg":
                if options.trg is not None:
                    api_dict["target.label"]=options.trg
            case "cl":
                if options.trg is not None:
                    api_dict["biosample_ontology.term_name"]=options.cl
                    api_dict["biosample_ontology.classification"]="cell line" 
            case "assembly":
                if options.trg is not None:
                    api_dict["target.label"]=options.gen
            case _:
                pass
# add default
    api_dict['perturbed']='false'
    api_dict['limit']='all'
    api_dict['type']='Experiment'
    api_dict['status']='released'

    base_url="https://www.encodeproject.org/search/"

    rs=requests.get(base_url,params=api_dict,headers=headers)
    print(api_dict)
    print(rs.headers)
    rj = rs.json()
    if rj['notification'] == "Success":
        return rj
    else: 
        print(rj['notification'] +": FATAL error")
        exit(1)


def DisplayENCODEquery(options):
    print("Query:")
    print ("=====================================")
    print(f"Organism : {options.organism}")
    print(f"Cell Line : {options.cl}")
    print(f"Genome : {options.gen}")
    print(f"Exp Type/Assay : {options.assay}")
    print(f"Target : {options.trg}")
    print(f"Keep archived analyses : {options.ka}")
    print ("===================================\n")

def choose_file(result,format,output_types,assembly,file_status,an_status,keep_arch=False):
    if result['output_type'] in output_types:
        if result['status']==file_status:
            if result['file_format']==format:
                if result['assembly']==assembly or assembly=="any":
                    for entry in result['analyses']:
                        if entry['status']==an_status or keep_arch==True:
                            return True

def bed_files(experiments,genome,keep_archived):
    DownloadUrl_l = [] 
    for x in experiments['@graph']:
        expr = str((x['@id']))
        tf_cl=x['biosample_summary']
        url = f"https://www.encodeproject.org{expr}"
        expr_r = requests.get(url, headers=headers)
        test = expr_r.json()
        for i,item in enumerate(test['files']):
            try:
                test['files'][i]['preferred_default']=="True"
            except KeyError:
                continue
            if choose_file(result=test['files'][i], output_types=[
                "optimal IDR thresholded peaks",
                "IDR thresholded peaks",
                "pseudoreplicated peaks",
                "conservative IDR thresholded peaks"
                ], format="bed", assembly=genome,
                file_status="released",an_status="released",
                keep_arch=keep_archived) == True:
                dl = item['href']
                accession = item['accession']
                tf_name = item['target'].replace("/targets/","").replace("/","")
                tf_genome = item['assembly']
                download_url = f'https://www.encodeproject.org{dl}'
                url_info =  f'https://www.encodeproject.org/files/{accession}'
                bed_file = {'url_info': url_info, 'download_url': download_url,
                            'target' : tf_name, 'cell_line': tf_cl,
                            'genome' : tf_genome, 'experiment_code': expr}
                print(f'found target "{tf_name}" in "{tf_cl}"')
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

def createdir(outdirname):
    if os.path.exists(outdirname):
        print(f'{outdirname} already present, skipping it...')
        exit(1)
    else:
        os.mkdir(outdirname)

if __name__ == '__main__':
    options = dloptions()
    skipd_opt=options.sd
    keep_arch_opt=options.ka
    if options.beyond_cell_line==True:
        biosample_opt='*'
        print('Extend to other cell lines is set True, so cell line is automatically set as all (i.e. *)')
        options.cl='*'
    else:
        biosample_opt='cell+line'
    DisplayENCODEquery(options)
    experiments = search_experiments(options)
    if options.gen=='*':
        gen_opt='any'
    else:
        gen_opt=options.gen
    results = bed_files(experiments=experiments,genome=gen_opt,keep_archived=keep_arch_opt)
    if options.outdir is not None:
        outputdir=options.outdir
    else:
        if options.trg=='*':
            outputdir="AllTargets"
        else:
            outputdir=options.trg
    createdir(outdirname=outputdir)
    if options.jd==True and options.assay == 'TF' and options.trg!="*" :
        jaspar = search_jaspar(tf=options.trg,tg=options.tg)
        jaspar_to_file(jaspar,options.outdir)
    with open(f'./{outputdir}/bed_files.txt', 'a') as f:
        json.dump(results,f,ensure_ascii=False, indent=4)
    os.chdir(outputdir)
    urls=[]
    for i in results:
        urls.append(i['download_url'])
    if skipd_opt==True:
        print("As skip-download was set, the above experiements won't be downloaded.")
    else:
        p = ThreadPool(int(options.tp))
        p.map(download,urls)
