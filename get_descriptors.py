import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--people_terms', required=True)

args = parser.parse_args()

def run_depparse(possible_marks, not_marks, word2dem, textbook_lines, title, outfile, nlp): 
	print(title)
	for line in textbook_lines:
    	doc = nlp(line)
    	prev_word = None
    	# get common noun descriptors
    	for token in doc:
    		word = token.text.lower()
    		target_term = token.head.text.lower()
    		if token in word2dem: 
	    		if token.pos_ != 'PROPN' and \
	            	token.pos_ != 'NOUN' and token.pos_ != 'PRON': continue
            	dem = word2dem[token]
            	if prev_word in possible_marks and word not in possible_marks: 
            		# word is marked, so add word to marked category
            		dem = word2dem[prev_word]

            	if token.dep_ == 'nsubj': 
            		if token.head.pos_ == 'VERB': 
            			outfile.write(title + ',' + word + ',' + dem + ',' + \
            				target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            			if prev_word in possible_marks and w in possible_marks:
            				# handle intersectionality if necessary
            				if dem != word2dem[prev_word]: 
            					outfile.write(title + ',' + prev_word + ',' + word2dem[prev_word] + ',' + \
            						target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            		elif token.head.pos_ == 'ADJ': 
            			outfile.write(title + ',' + word + ',' + dem + ',' + \
            				target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            			if prev_word in possible_marks and w in possible_marks:
            				if dem != word2dem[prev_word]: 
            					outfile.write(title + ',' + prev_word + ',' + word2dem[prev_word] + ',' + \
            						target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            	if token.dep_ == 'nsubjpass': 
            		if token.head.pos_ == 'VERB': 
            			outfile.write(title + ',' + word + ',' + dem + ',' + \
            				target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            			if prev_word in possible_marks and w in possible_marks:
            				if dem != word2dem[prev_word]: 
            					outfile.write(title + ',' + prev_word + ',' + word2dem[prev_word] + ',' + \
            						target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            	if token.dep_ == 'obj': 
            		if token.head.pos_ == 'VERB': 
            			outfile.write(title + ',' + word + ',' + dem + ',' + \
            				target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            			if prev_word in possible_marks and w in possible_marks:
            				if dem != word2dem[prev_word]: 
            					outfile.write(title + ',' + prev_word + ',' + word2dem[prev_word] + ',' + \
            						target_term + ',' + token.head.pos_ + ',' + token.dep_ + '\n')
            if token.dep_ == 'amod':
            	if target_term in word2dem: 
            		if token.head.pos_ != 'PROPN' and \
	            	token.head.pos_ != 'NOUN' and token.head.pos_ != 'PRON': continue
	            	dem = word_cats[target_term]
	            	prev_target_term = 'xxxxxx'
	            	prev_index = token.head.i - 1
	            	if prev_index >= 0: 
	            		prev_target_term = doc[prev_index]
	            	if prev_target_term in possible_marks and target_term not in possible_marks:
			            # term is marked, assign to marker's category
			            dem = word_cats[prev_target_term]
			        outfile.write(title + ',' + target_term + ',' + dem + ',' + \
            						word + ',' + token.pos_ + ',' + token.dep_ + '\n')
			        if prev_target_term in possible_marks and target_term in possible_marks:
			        	if dem != word2dem[prev_target_term]:
			        		outfile.write(title + ',' + prev_target_term + ',' + word2dem[prev_target_term] + ',' + \
            						word + ',' + token.pos_ + ',' + token.dep_ + '\n')
			prev_word = token
		# get famous people descriptors
		'''
		for ent in doc.ents: 
			for ent in doc.ents: 
                if (ent.label_ == 'PERSON' and not ent.text[0].isdigit()): 
                    curr_entity = ent.text

			w = dic["form"].lower()
            rel = dic["deprel"]
            target = dic["head"]
            target_term = d[str(i)][target - 1]["form"].lower()
            target_tag = d[str(i)][target - 1]["upostag"]
            if dic['entity_type'] == 'PERSON': 
                if dic['full_entity'] not in famous_people: continue
                if rel == 'nsubj':
                    if target_tag == 'VERB':
                        subj_v[dic['full_entity']].append((target_term, (i, idx)))
                    elif target_tag == 'ADJ':
                        adjs[dic['full_entity']].append((target_term, (i, idx)))
                if rel == 'nsubj:pass':
                    if target_tag == 'VERB':
                        pass_v[dic['full_entity']].append((target_term, (i, idx)))
                if rel == 'obj':
                    if target_tag == 'VERB':
                        obj_v[dic['full_entity']].append((target_term, (i, idx)))
            if rel == 'amod':
                target_entity = d[str(i)][target - 1]["entity_type"]
                if target_entity == 'PERSON':
                    if d[str(i)][target - 1]['full_entity'] not in famous_people: continue
                    adjs[d[str(i)][target - 1]['full_entity']].append((w, (i, target-1)))
    '''

def main(): 
	possible_marks, not_marks = split_terms_into_sets(args.people_terms)
	word2dem = get_word_to_category(args.people_terms)
	# load spacy
    nlp = spacy.load("en_core_web_sm")

    # load books
    books = get_book_txts(args.input_dir, splitlines=True)
    outfile = codecs.open(os.path.join(args.output_dir, 'people_descriptors.csv'), 'w', encoding='utf-8')
    for title, textbook_lines in books.items():
		run_depparse(possible_marks, not_marks, word2dem, textbook_lines, title, outfile, nlp)
	outfile.close()

if __name__ == '__main__':
    main()