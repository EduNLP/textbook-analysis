#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
import gensim.corpora as corpora
from gensim.models.wrappers import LdaMallet
from gensim.models import CoherenceModel
from helpers import *
import nltk
import json

parser = argparse.ArgumentParser()

parser.add_argument('--mallet_dir', required=True, help="Location of MALLET binary file.")
parser.add_argument('--input_dir', required=True, help="Directory of input text files.")
parser.add_argument('--output_dir', required=True, help="Directory for the topic model.")
parser.add_argument('--num_topics', default=100, type=int, help="Number of topics to induce.")
parser.add_argument('--stem', action='store_true', help="Whether to stem words before running the topic model "
                                                        "(in the paper, we do).")

args = parser.parse_args()


def get_topics(num, corpus, id2word, output_dir, all_sentences):
    print(num)
    ldamallet = LdaMallet(args.mallet_dir,
                          corpus=corpus,
                          num_topics=num,
                          prefix=output_dir + "/" + str(num),
                          workers=4,
                          id2word=id2word,
                          iterations=1000,
                          random_seed=42)
    coherence_model_ldamallet = CoherenceModel(model=ldamallet,
                                               texts=all_sentences,
                                               dictionary=id2word,
                                               coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print('\nCoherence Score: ', coherence_ldamallet)
    keywords = {i: ", ".join([word for word, prop in ldamallet.show_topic(i)]) for i in range(ldamallet.num_topics)}
    with open(output_dir + "/" + str(num) + '_words.json', 'w') as f:
        f.write(json.dumps(keywords))
    ldamallet.save(output_dir + "/" + str(num))
    #ldamallet.show_topics(num_topics=num, formatted=True)
    return coherence_ldamallet


def main():
    print("Loading books...")
    books = get_book_txts(args.input_dir, splitlines=False)

    print("Cleaning and combining texts...")
    all_sentences = []
    start_end = []
    prev = 0
    for title, book in books.items():
        print(title)
        sents = nltk.sent_tokenize(book)
        start = prev
        for i, s in enumerate(sents):
            all_sentences.append(clean_text(s, stem=args.stem))
        end = start + len(sents) - 1
        start_end.append((title, start, end))
        prev = end + 1

    start_end_dict = {}
    for tup in start_end:
        start_end_dict[tup[0]] = (tup[1], tup[2])
    with open(args.output_dir + '/book_start_end.json', 'w') as f:
        f.write(json.dumps(start_end_dict))

    print("%d sentences total" % len(all_sentences))

    print("Creating dictionary...")
    id2word = corpora.Dictionary(all_sentences)
    id2word.save(args.output_dir + '/dictionary.dict')

    print("Getting term-document frequencies...")
    corpus = [id2word.doc2bow(t) for t in all_sentences]

    print("Running topic model with %d topics..." % args.num_topics)
    get_topics(args.num_topics, corpus, id2word, args.output_dir, all_sentences)


if __name__ == '__main__':
    main()




