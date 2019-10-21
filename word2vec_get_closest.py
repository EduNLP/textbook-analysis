#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
import os
import numpy as np
from helpers import *
parser = argparse.ArgumentParser()

parser.add_argument('--input_file', default=None, help="Text file with input words.")
parser.add_argument('--words', default=None, help="Comma-separated list of input words.")
parser.add_argument('--word2vec_dir', required=True, help="Directory for model output.")

args = parser.parse_args()

def get_closest(queries, models, vocab, idx2word):
    cosines = []
    for m in models:
        cosines.append([np.mean([m.similarity(q, word) for q in queries]) for word in vocab])
    cosines = np.mean(np.array(cosines), axis=0)
    return [(idx2word[idx], cosines[idx]) for idx in cosines.argsort()[-20:][::-1]]

def main():
    # Get queries
    if args.input_file:
        with open(args.input_file) as f:
            queries = f.read().splitlines()
    elif args.words:
        queries = [w.strip() for w in args.words.split(",")]
    else:
        print("Either --input_file or --words must be specified.")
        return

    print("Loading models...")
    filelist = []
    for subdir, dirs, files in os.walk(args.word2vec_dir):
        for file in files:
            filelist.append(os.path.join(subdir, file))
    models = get_models(filelist)

    # Get vocab
    vocab = set(models[0].vocab)
    for m in models:
        vocab &= set(m.vocab)

    # Remove queries not in vocab
    queries = set(queries)
    not_in_vocab = queries - vocab
    if not_in_vocab:
        print("Not in vocab:", not_in_vocab)
    queries = list(queries - not_in_vocab)
    vocab = list(vocab)
    idx2word = {i: w for i, w in enumerate(vocab)}

    print("Getting most similar words...")
    closest = get_closest(queries, models, vocab, idx2word)
    for (w, c) in closest:
        print("%s %.2f" % (w, c))


if __name__ == '__main__':
    main()


