#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helpers import *
import spacy
import neuralcoref
import argparse
import os
parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True)
parser.add_argument('--output_dir', required=True)

args = parser.parse_args()

possessives = {'his', 'her', 'its', 'their', 'hers', 'theirs'}

def lowercase_if_not_entity(span):
    first_token = span[0]
    if first_token.ent_type_ == '' and first_token.is_sent_start and first_token.text.istitle():
        return span.text[0].lower() + span.text[1:]
    return span.text

def check_possessive(token, sub):
    if sub in possessives:
        return ''
    text = token.text.lower()
    if text in possessives:
        if sub[-1] == 's':
            return "'"
        else:
            return "'s"
    return ''

def get_correct_case(coref, main_uncased, main_original):
    if coref[0].is_sent_start:
        return main_original.text[0].upper() + main_original.text[1:]
    else:
        return main_uncased

def get_resolved(doc, clusters):
    ''' modified based on https://github.com/huggingface/neuralcoref/blob/master/neuralcoref/neuralcoref.pyx'''
    ''' Return a list of utterrances text where the coref are resolved to the most representative mention'''
    resolved = list(tok.text_with_ws for tok in doc)
    for cluster in clusters:
        for coref in cluster:
            main_mention = lowercase_if_not_entity(cluster.main)
            if coref != cluster.main:
                resolved[coref.start] = get_correct_case(coref, main_mention, cluster.main) + check_possessive(
                    coref, main_mention) + doc[coref.end - 1].whitespace_
                for i in range(coref.start + 1, coref.end):
                    resolved[i] = ""
    return ''.join(resolved)


def main():
    # Load your usual SpaCy model (one of SpaCy English models)
    nlp = spacy.load('en_core_web_sm')

    # Add neural coref to SpaCy's pipe
    neuralcoref.add_to_pipe(nlp, blacklist=True)

    # load books
    books = get_book_txts(args.input_dir, splitlines=True)

    print('Resolving coref...')
    os.makedirs(args.output_dir, exist_ok=True)
    for title, textbook_lines in books.items():
        print(title)
        with codecs.open(os.path.join(args.output_dir, title), 'w', encoding='utf-8') as f:
            for line in textbook_lines:
                doc = nlp(line)
                f.write(get_resolved(doc, doc._.coref_clusters) + '\n')

if __name__ == '__main__':
    main()





