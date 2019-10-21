#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
from gensim.models import phrases, word2vec
from helpers import *
import nltk
import numpy as np
import codecs
from collections import Counter
from nltk.corpus import stopwords
import argparse
import os
parser = argparse.ArgumentParser()

parser.add_argument('--input_dir', required=True, help="Directory of input text files.")
parser.add_argument('--output_dir', required=True, help="Directory for model output.")
parser.add_argument('--num_runs', default=50, type=int, help="Number of word2vec training runs")
parser.add_argument('--dim', default=100, type=int, help="Dimensionality of embeddings.")
parser.add_argument('--window', default=5, type=int, help="Window size for word2vec.")
parser.add_argument('--stem', action='store_true', help="Whether to stem words (in the paper, we don't).")

args = parser.parse_args()

stopwords = set(stopwords.words('english'))

def get_sentences(book):
    sents = nltk.sent_tokenize(book)
    return [clean_text(s, stem=args.stem, remove_stopwords=False) for s in sents]

def run_on_all_books(books, bootstrap=True):
    """Runs word2vec training on data.

    Args:
        books: dictionary of titles to text (str)
        bootstrap: whether to bootstrap sample from the sentences

    """

    # Combine all text into a list of sentences
    print("Getting sentences...")
    all_sentences = []
    for title, book in books.items():
        all_sentences.extend(get_sentences(book))

    # Create model
    bigrams = phrases.Phrases(all_sentences, min_count=5, delimiter=b' ', common_terms=stopwords)

    # Create vocabulary of bigrams
    print("Creating vocabulary...")
    vocab = [w for sent in bigrams[all_sentences] for w in sent]
    vocab = [w for w, count in Counter(vocab).most_common() if count >= 5]

    # Save vocab
    with codecs.open(os.path.join(args.output_dir, 'vocab.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(vocab))

    # Run word2vec model
    for run_idx in range(args.num_runs):
        print("Run #%d" % run_idx)
        if bootstrap:
            data = bigrams[np.random.choice(all_sentences, len(all_sentences), replace=True)]
        else:
            data = bigrams[all_sentences]
        model = word2vec.Word2Vec(data, size=args.dim, window=args.window, sg=1, min_count=5, workers=10)
        model.wv.save(os.path.join(args.output_dir, str(run_idx) + '.wv'))

def main():
    books = get_book_txts(args.input_dir, splitlines=False)
    os.makedirs(args.output_dir, exist_ok=True)
    run_on_all_books(books)


if __name__ == '__main__':
    main()



