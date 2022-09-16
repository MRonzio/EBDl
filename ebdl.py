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

def search_experiments(organism, exp_type, exp, cl, genome,biosample): 
    api_dict = {'organism': 'replicates.library.biosample.donor.organism.scientific_name',
                'assay' : 'assay_title',
                'exp': 'target.label',
                'cell_line':'biosample_ontology.term_name',
                'genome':'assembly',
                'biosample':'biosample_ontology.classification'
                }

    r = (f"https://www.encodeproject.org/search/?type=Experiment"\
        f"&{api_dict['organism']}={organism}"\
        f"&{api_dict['assay']}={exp_type}&status=released"\
        f"&{api_dict['exp']}={exp}"\
        f"&{api_dict['genome']}={genome}"\
        f"&{api_dict['biosample']}={biosample}"\
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
    print("Query:")
    print ("=====================================")
    print(f"Organism : {set_options.organism}")
    print(f"Cell Line : {set_options.cl}")
    print(f"Genome : {set_options.gen}")
    print(f"Exp Type : {set_options.exp_type}")
    print(f"Exp : {set_options.exp}")
    print(f"Keep archived analyses : {set_options.ka}")
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

def createdir(exp_name):
    if os.path.exists(exp_name):
        print(f'{exp_name} already present, skipping it...')
        exit(1)
    else:
        os.mkdir(exp_name)

if __name__ == '__main__':
    options = dloptions()
    jd_opt=options.jd
    skipd_opt=options.sd
    keep_arch_opt=options.ka
    if options.beyond_cell_line==True:
        biosample_opt='*'
        print('Extend to other cell lines is set True, so cell line is automatically set as all (i.e. *)')
        options.cl='*'
    else:
        biosample_opt='cell+line'
    DisplayENCODEquery(set_options=options)
    exp_type_opt=options.exp_type + '+ChIP-seq'        
    experiments = search_experiments(organism=options.organism,
                                     exp_type=exp_type_opt,
                                     exp=options.exp,
                                     cl=options.cl,
                                     genome=options.gen,
                                     biosample=biosample_opt)
    if options.gen=='*':
        gen_opt='any'
    else:
        gen_opt=options.gen
    results = bed_files(experiments=experiments,genome=gen_opt,keep_archived=keep_arch_opt)
    if options.exp=='*':
        exp_opt='all'
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
    if skipd_opt==True:
        print("As skip-download was set, the above experiements won't be downloaded.")
    else:
        p = ThreadPool(int(options.tp))
        p.map(download,urls)
