'''
Standardize named entity names
0. Run NER on data. 
1. Replace aliases with standardized wikidata names.
2. Find top 100 most common famous people. 
This means from here on out we only focus on them and we're allowed to 
ignore noisy entities, e.g. "Response Roosevelt." 
3. Matching last names to full names. As we move through the text and 
find named entities, we keep a running dictionary of last name to full names. 
So, if we see "Theodore Roosevelt" we have {Roosevelt: Theodore Roosevelt}, and 
so if we see just "Roosevelt" later, we look it up in the dictionary. 
This dictionary is updated so each last name only has one full name. 
So, if we move later on in history, eventually we will hit someone named 
"Franklin Roosevelt" and the value for the key "Roosevelt" will become 
{ Roosevelt: Franklin Roosevelt }. This means a last name is paired with 
the most recent full name related to it.  
'''

import argparse
from helpers import *
import os
import urllib.parse
from urllib.request import urlopen
from collections import Counter
import spacy
import json

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--ner_dir', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--redo_intermediates', default=False, 
    help='True/False: calculate famous_people and full2wikiname.json.')

args = parser.parse_args()

def get_official_name(entity): 
    entity = entity.replace("\"", "").replace("—", "").replace("\\","")
    entity = entity.strip()
    url_prefix = "https://query.wikidata.org/sparql?format=json&query="
    query = urllib.parse.quote("SELECT ?item ?itemLabel WHERE {" + \
    "?item wdt:P31 wd:Q5." + \
    "?item ?label \"" + entity + "\"@en ." + \
    "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". }" + \
    "}", safe='')
    url = url_prefix + query
    res = json.loads(urlopen(url).read())
    cands = []
    if len(res['results']['bindings']) > 0:
        for i in range(len(res['results']['bindings'])): 
            wikiID = res['results']['bindings'][i]['item']['value'].split('/')[-1]
            name = res['results']['bindings'][i]['itemLabel']['value'].split('/')[-1]
            cands.append((name, wikiID)) 
    return cands

def get_full2wikiname_and_famous_people(books, nlp, redo=args.redo_intermediates): 
    if redo or not os.path.isfile('./results/full2wikiname.json') or \
        not os.path.isfile('./wordlists/famous_people'): 
        if os.path.isfile('./results/full2wikiname.json'): 
            with open('./results/full2wikiname.json', 'r') as infile: 
                full2wikiname = json.load(infile)
        else: 
            full2wikiname = {}
        
        famous_counter = Counter()
        print("Getting wikidata aliases and most common people...")
        for title, textbook_lines in books.items():
            print(title)
            for line in textbook_lines: 
                doc = nlp(line)
                for ent in doc.ents: 
                    if (ent.label_ == 'PERSON' and not ent.text[0].isdigit()): 
                        curr_entity = ent.text
                        if ent.text in full2wikiname: 
                            curr_entity = full2wikiname[ent.text]
                        elif ent.text not in full2wikiname and len(ent.text.split()) > 1: 
                            cands = get_official_name(ent.text)
                            if len(cands) == 1: 
                                full2wikiname[ent.text] = cands[0][0]
                            else: 
                                # do not match ambiguous terms
                                full2wikiname[ent.text] = ent.text
                            curr_entity = full2wikiname[ent.text]
                        else: # ent.text not in full2wikiname and ent.text is single token
                            full2wikiname[ent.text] = ent.text
                        famous_counter[curr_entity] += 1
        famous_people = set()
        for tup in famous_counter.most_common(100):
            famous_people.add(tup[0])
        
        with open('./results/full2wikiname.json', 'w') as outfile: 
            json.dump(full2wikiname, outfile)

        # save famous people for getting descriptors later
        with open('./wordlists/famous_people', 'w') as outfile: 
            for person in famous_people: 
                outfile.write(person + '\n')
    else: 
        print("Retrieving saved intermediate files...")
        with open('./results/full2wikiname.json', 'r') as infile: 
            full2wikiname = json.load(infile)

        famous_people = set()
        # save famous people for getting descriptors later
        with open('./wordlists/famous_people', 'r') as infile: 
            for line in infile: 
                famous_people.add(line.strip())

    return famous_people, full2wikiname

def main(): 
    nlp = spacy.load("en_core_web_sm")
    books = get_book_txts(args.input_dir, splitlines=True)

    famous_people, full2wikiname = get_full2wikiname_and_famous_people(books, nlp)

    os.makedirs(args.ner_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    print("Writing output files...")
    for title, textbook_lines in books.items():
        print(title)
        entity_counter = Counter() # this time matching last names to common full names
        name_map = {} # last : full
        with open(os.path.join(args.ner_dir, title), 'w') as outfile: 
            for line in textbook_lines: 
                doc = nlp(line)
                replacements = {} # start : (entity, end)
                for ent in doc.ents: 
                    if (ent.label_ == 'PERSON' and not ent.text[0].isdigit()): 
                        curr_entity = ent.text
                        if ent.text in full2wikiname and ent.text != full2wikiname[ent.text]: 
                            # replace with wikiname
                            print("REPLACE", curr_entity, full2wikiname[ent.text])
                            curr_entity = full2wikiname[ent.text]
                        if len(curr_entity.split()) == 1: 
                            if curr_entity in name_map: 
                                # replace last name with latest full name
                                curr_entity = name_map[curr_entity]
                        elif curr_entity in famous_people: 
                            # name map should only contain famous people
                            last = curr_entity.split()[-1]
                            name_map[last] = curr_entity
                        entity_counter[curr_entity] += 1
                        if curr_entity != ent.text: 
                            replacements[ent.start_char] = (curr_entity, ent.end_char)
                new_line = ''
                curr_end = -1
                for idx, char in enumerate(line): 
                    if idx in replacements: 
                        curr_end = replacements[idx][1]
                        new_line += replacements[idx][0] 
                    elif idx >= curr_end: 
                        new_line += char
                outfile.write(new_line + '\n')
        with open(os.path.join(args.output_dir, title), 'w') as outfile: 
            for tup in entity_counter.most_common(100):
                outfile.write(tup[0] + ',' + str(tup[1]) + '\n')

if __name__ == '__main__':
    main()