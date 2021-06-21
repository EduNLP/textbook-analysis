import argparse
from helpers import *
import spacy
import os
import math
from spacy.pipeline import merge_entities

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--people_terms', required=True)

args = parser.parse_args()

def run_depparse(possible_marks, word2dem, famous_people, 
    textbook_lines, title, nlp): 
    '''
    Get adjectives and verbs associated with frequent named entities
    and common nouns referring to people.
    @inputs: 
    - possible_marks: words that may mark common nouns with a social group, e.g. "black"
    - word2dem: word to demographic category
    - famous_people: a set of popular named entities
    - textbook_lines: strings of textbook content in a list
    - title: title of book
    - outfile: opened file
    - nlp: spacy pipeline
    '''
    print("Running dependency parsing for", title)
    # Break up every textbook into 5k line chunks to avoid spaCy's text length limit 
    j = 0
    k = 0
    num_lines = len(textbook_lines)
    res = []
    for i in range(0, num_lines, 5000):
        chunk = '\n'.join(textbook_lines[i:i+5000])
        doc = nlp(chunk)
        k += 1
        print("Finished part", k, "of", math.ceil(num_lines/5000))
        prev_word = None
        for token in doc:
            j += 1
            word = token.text.lower()
            target_term = token.head.text.lower()
            # non-named people
            if len(word2dem[word]) > 0: 
                if token.pos_ != 'PROPN' and \
                    token.pos_ != 'NOUN' and token.pos_ != 'PRON': continue
                dem = word2dem[word]
                if prev_word in possible_marks and word not in possible_marks: 
                    # word is marked, so add word to marked category
                    dem = word2dem[prev_word]

                if token.dep_ == 'nsubj' and (token.head.pos_ == 'VERB' or token.head.pos_ == 'ADJ'): 
                    res.append((str(j), title, word, dem, target_term, token.head.pos_, token.dep_))
                    if prev_word in possible_marks and word in possible_marks:
                        # handle intersectional markers if present
                        other_dem = set(word2dem[prev_word]) - set(dem)
                        if len(other_dem) > 0: 
                            res.append((str(j), title, prev_word, other_dem, target_term, 
                                token.head.pos_, token.dep_))
                if token.dep_ == 'nsubjpass' and token.head.pos_ == 'VERB': 
                    res.append((str(j), title, word, dem, target_term, token.head.pos_, token.dep_))
                    if prev_word in possible_marks and word in possible_marks:
                        other_dem = set(word2dem[prev_word]) - set(dem)
                        if len(other_dem) > 0: 
                            res.append((str(j), title, prev_word, other_dem, target_term, 
                                token.head.pos_, token.dep_))
                if (token.dep_ == 'obj' or token.dep_ == 'dobj') and token.head.pos_ == 'VERB': 
                    res.append((str(j), title, word, dem, target_term, token.head.pos_, token.dep_))
                    if prev_word in possible_marks and word in possible_marks:
                        other_dem = set(word2dem[prev_word]) - set(dem)
                        if len(other_dem) > 0: 
                            res.append((str(j), title, prev_word, other_dem, target_term, 
                                token.head.pos_, token.dep_))
            # named people
            if token.ent_type_ == 'PERSON':
                if word in famous_people: 
                    if token.dep_ == 'nsubj' and (token.head.pos_ == 'VERB' or token.head.pos_ == 'ADJ'): 
                        res.append((str(j), title, word, 'named', target_term, token.head.pos_, token.dep_))
                    if token.dep_ == 'nsubjpass' and token.head.pos_ == 'VERB': 
                        res.append((str(j), title, word, 'named', target_term, token.head.pos_, token.dep_))
                    if (token.dep_ == 'obj' or token.dep_ == 'dobj') and token.head.pos_ == 'VERB': 
                        res.append((str(j), title, word, 'named', target_term, token.head.pos_, token.dep_))

            # adjectival modifier 
            if token.dep_ == 'amod':
                # non-named people
                if len(word2dem[target_term]) > 0:
                    if token.head.pos_ != 'PROPN' and \
                    token.head.pos_ != 'NOUN' and token.head.pos_ != 'PRON': continue
                    dem = word2dem[target_term]
                    prev_target_term = 'xxxxxx'
                    prev_index = token.head.i - 1
                    if prev_index >= 0: 
                        prev_target_term = doc[prev_index].text.lower()
                    if prev_target_term in possible_marks and target_term not in possible_marks:
                        # term is marked, assign to marker's category
                        dem = word2dem[prev_target_term]
                    res.append((str(j), title, target_term, dem, word, token.pos_, token.dep_))
                    if prev_target_term in possible_marks and target_term in possible_marks:
                        other_dem = set(word2dem[prev_target_term]) - set(dem)
                        if len(other_dem) > 0: 
                            res.append((str(j), title, prev_target_term, other_dem, 
                                word, token.pos_, token.dep_))
                # named people
                if token.head.ent_type_ == 'PERSON' and target_term in famous_people:
                    res.append((str(j), title, target_term, 'named', word, token.pos_, token.dep_))

            prev_word = word
    return res

def main(): 
    possible_marks, not_marks = split_terms_into_sets(args.people_terms)
    word2dem = get_word_to_category(args.people_terms)
    famous_people = set()
    with open('./wordlists/famous_people', 'r') as infile: 
        for line in infile: 
            famous_people.add(line.strip().lower())
    # load spacy
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(merge_entities)
    # load books
    books = get_book_txts(args.input_dir, splitlines=True)
    for title, textbook_lines in books.items():
        res = run_depparse(possible_marks, word2dem, famous_people, 
            textbook_lines, title, nlp)
    outfile = codecs.open(os.path.join(args.output_dir, 'people_descriptors.csv'), 'w', encoding='utf-8')
    for tup in res: 
        if type(tup[3]) == list or type(tup[3]) == set: 
            for d in tup[3]: 
                outfile.write(tup[0] + ',' + tup[1] + ',' + tup[2] + ',' + d + ',' + \
                                tup[4] + ',' + tup[5] + ',' + tup[6] + '\n')
        else: 
            outfile.write(tup[0] + ',' + tup[1] + ',' + tup[2] + ',' + tup[3] + ',' + \
                                tup[4] + ',' + tup[5] + ',' + tup[6] + '\n')
    outfile.close()

if __name__ == '__main__':
    main()