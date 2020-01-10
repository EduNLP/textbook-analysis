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

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--ner_dir', required=True)
parser.add_argument('--output_dir', required=True)

def get_full2wikiname(): 
	# TODO: get wikidata aliases
    with open('../logs/full2wikiname.json', 'r') as infile: 
        full2wikiname = json.load(infile)
    # limit every full to only match to one wikiname
    for full in full2wikiname: 
        if len(full2wikiname[full]) > 1: 
            if full not in full2wikiname: 
                # should print nothing
                print(full, full2wikiname[full])
            else: 
                full2wikiname[full] = full
        else: 
            full2wikiname[full] = full2wikiname[full][0]
    return full2wikiname

def main(): 
	full2wikiname = {}
	books = get_book_txts(args.input_dir, splitlines=True)
	famous_counter = Counter()
	print("Getting wikidata aliases and most common people...")
	for title, textbook_lines in books.items():
		print(k)
        for line in textbook_lines: 
            doc = nlp(line)
            for ent in doc.ents: 
                if (ent.label_ == 'PERSON' and not ent.text[0].isdigit()): 
                    curr_entity = ent.text
                    # TODO maybe look for wikidata aliases here
                    # TODO to save time, cache the people we've already looked up
                    if ent.text in full2wikiname and ent.text != full2wikiname[ent.text]: 
                        curr_entity = full2wikiname[ent.text]
                    famous_counter[curr_entity] += 1
    famous_people = set()
    for tup in famous_counter.most_common(100):
        famous_people.add(tup[0])

    # save famous people for getting descriptors later
    with open('./wordlists/famous_people', 'w') as outfile: 
    	for person in famous_people: 
    		outfile.write(person + '\n')

    print("Writing output files...")
    for title, textbook_lines in books.items():
        print(k)
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