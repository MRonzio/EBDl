#!/usr/bin/python3
import requests
import pprint
import argparse

headers = {'accept': 'application/json'}

################################################################################
# COMMAND LINE OPTIONS
def cli_options():
    parser = argparse.ArgumentParser(description='EBDl encode bed downloader')
    parser.add_argument('-o', dest='organism', default='Homo+sapiens', help='organism')
    parser.add_argument('-f', dest='tf', default='CTCF', help='transcription factor')
    parser.add_argument('-l', default='K562', dest='cl', help='Cell line')
    return parser.parse_args()


def search_experiments(organism, tf, cl): 
    api_dict = { 'organism': 'replicates.library.biosample.donor.organism.scientific_name','tf': 'target.label','cell_line':'biosample_ontology.term_name'}
    r = requests.get(f"https://www.encodeproject.org/search/?type=Experiment&{api_dict['organism']}={organism}&assay_title=TF+ChIP-seq&status=released&{api_dict['tf']}={tf}&biosample_ontology.classification=cell+line&{api_dict['cell_line']}={cl}",headers=headers)
    return r.json()


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

    
if __name__ == '__main__':
    options = cli_options()
    experiments = search_experiments(organism=options.organism, tf=options.tf, cl=options.cl)
    results = bed_files(experiments=experiments)
    pprint.pprint(results)

