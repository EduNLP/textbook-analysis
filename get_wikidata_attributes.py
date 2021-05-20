'''
Get Wikidata attributes for names
'''

import argparse
from helpers import *
import os
import urllib.parse
from urllib.request import urlopen
from collections import Counter
import spacy
import json
import codecs

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--output_dir', required=True)

args = parser.parse_args()

def query_for_multiple_properties(person): 
    return urllib.parse.quote("SELECT ?propLabel ?propertyLabel WHERE { " + \
      "SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". } " + \
      "{wd:" + person + " wdt:P21 ?property. " + \
      "?name ?ref wdt:P21. " + \
      "?name rdfs:label ?propLabel} " + \
      "UNION " + \
      "{wd:" + person + " wdt:P106 ?property. " + \
      "?name ?ref wdt:P106. " + \
      "?name rdfs:label ?propLabel} " + \
      "UNION " + \
      "{wd:" + person + " wdt:P172 ?property. " + \
      "?name ?ref wdt:P172. " + \
      "?name rdfs:label ?propLabel} " + \
      "FILTER((LANG(?propLabel)) = \"en\") " + \
      "} LIMIT 100", safe="")

def retrieve_wikidata(entity): 
    """
    Input 
    """
    entity = entity.replace("\"", "").replace("—", "").replace("\\","")
    entity = entity.strip()
    url_prefix = "https://query.wikidata.org/sparql?format=json&query="
    query = urllib.parse.quote("SELECT ?item ?itemLabel WHERE {" + \
    "?item wdt:P31 wd:Q5." + \
    "?item ?label \"" + entity + "\"@en ." + \
    "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". }" + \
    "}", safe='')
    print(entity)
    url = url_prefix + query
    res = json.loads(urlopen(url).read())
    cands = []
    if len(res['results']['bindings']) > 0:
        wikiID = res['results']['bindings'][0]['item']['value'].split('/')[-1]
        name = res['results']['bindings'][0]['itemLabel']['value'].split('/')[-1]
        person_dict = {}
        person_dict['name'] = name
        person_dict['wikiID'] = wikiID
        query_for_multiple_properties(wikiID)
        person_url = url_prefix + query_for_multiple_properties(wikiID)
        response = urlopen(person_url)
        result = json.loads(response.read())
        for item in result['results']['bindings']: 
            label = item["propLabel"]["value"]
            prop_val = item["propertyLabel"]["value"]
            if label not in person_dict: 
                person_dict[label] = [prop_val]
            else: 
                person_dict[label].append(prop_val)
        cands.append(person_dict)
    return cands


def main():
    wikidata_dict = {}
    num_ambig = 0
    for f in os.listdir(args.input_dir): 
        with open(os.path.join(args.input_dir, f), 'r', encoding='utf-8') as infile: 
            for line in infile: 
                contents = line.strip().split(',')
                count = contents[1]
                entity = contents[0]
                if entity in wikidata_dict:
                    continue
                if len(entity.split()) > 1: 
                    cands = retrieve_wikidata(entity) 
                    if len(cands) > 1: num_ambig += 1
                    wikidata_dict[entity] = cands
    print("Number of entities total", len(wikidata_dict))
    print("Number of entities with multiple wikidata entries:", num_ambig) 
    with open(os.path.join(args.output_dir, 'wikidata_attributes.csv'), 'w') as outfile: 
        outfile.write('entity,name,ID,race/ethnicity,gender,occupation\n')
        for entity in wikidata_dict: 
            entries = wikidata_dict[entity]
            for entry in entries: 
                outfile.write(entity + ',')
                outfile.write(entry['name'] + ',')
                outfile.write(entry['wikiID'] + ',')
                if 'ethnic group' in entry: 
                    outfile.write('|'.join(entry['ethnic group']) + ',')
                else: 
                    outfile.write('None,')
                if 'sex or gender' in entry: 
                    outfile.write('|'.join(entry['sex or gender']) + ',')
                else: 
                    outfile.write('None,')
                if 'occupation' in entry: 
                    outfile.write('|'.join(entry['occupation']))
                else: 
                    outfile.write('None')
                outfile.write('\n')


if __name__ == '__main__':
    main()
