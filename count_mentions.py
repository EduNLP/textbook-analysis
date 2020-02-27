import spacy
from helpers import *
import argparse
import os
import codecs
from collections import Counter

parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--people_terms', required=True)

args = parser.parse_args()

def main():
    possible_marks, not_marks = split_terms_into_sets(args.people_terms)
    word2dem = get_word_to_category(args.people_terms)

    # load spacy
    nlp = spacy.load("en_core_web_sm")

    # load books
    books = get_book_txts(args.input_dir, splitlines=True)

    print('Counting groups of people...')
    os.makedirs(args.output_dir, exist_ok=True)
    with codecs.open(os.path.join(args.output_dir, 'people_mentions.csv'), 'w', encoding='utf-8') as f:
        for title, textbook_lines in books.items():
            print(title)
            dem_dict = Counter() # demographic : count
            for line in textbook_lines:
                doc = nlp(line)
                prev_word = None
                for token in doc: 
                    word = token.text.lower()
                    # only look at nouns
                    if token.pos_ != 'PROPN' and \
                        token.pos_ != 'NOUN' and token.pos_ != 'PRON': continue
                    if word in possible_marks:
                        dem_dict[word2dem[word]] += 1
                        if prev_word in possible_marks:
                            # count previous word as well
                            # e.g. "black women"
                            dem_dict[word2dem[prev_word]] += 1
                    elif word in not_marks:
                        if prev_word not in possible_marks: 
                            dem_dict[word2dem[word]] += 1
                        else: 
                            # count previous word but not unmarked word
                            dem_dict[word2dem[prev_word]] += 1
                    prev_word = word
            for demographic in dem_dict: 
                f.write(title + ',' + demographic + ',' + str(dem_dict[demographic]) + '\n')

if __name__ == '__main__':
    main()