#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
import os
import numpy as np
import json
import pandas as pd
from helpers import *
from scipy.stats import ttest_ind
parser = argparse.ArgumentParser()

parser.add_argument('--queries', default=None, required=True, help="Dictionary file of topic names to queries.")
parser.add_argument('--words1', default=None, required=True, help="Input file with words referring to group 1.")
parser.add_argument('--words2', default=None, required=True, help="Input file with words referring to group 2.")
parser.add_argument('--name1', default="Group1", help="Name for group 1.")
parser.add_argument('--name2', default="Group2", help="Name for group 2.")
parser.add_argument('--word2vec_dir', required=True, help="Directory of models.")
parser.add_argument('--output_file', default="results/word2vec_cosines.csv", help="Output csv file.")

args = parser.parse_args()

def get_cosines(words1, words2, queries, models):
    df_w1 = []
    df_w2 = []
    df_q = []
    df_type = []
    df_pvals = []
    for key, values in queries.items():
        for q in values:
            vals1 = [m.similarity(word1, q) for m in models for word1 in words1]
            vals2 = [m.similarity(word2, q) for m in models for word2 in words2]
            df_w1.append(np.mean(vals1))
            df_w2.append(np.mean(vals2))
            df_q.append(q)
            df_type.append(key)
            df_pvals.append(ttest_ind(vals1, vals2)[1])
    df = pd.DataFrame({args.name1: df_w1, args.name2: df_w2, 'query': df_q, 'word category': df_type, "p value": df_pvals})
    return df

def filter_words(words, vocab):
    words = set(words)
    not_in_vocab = words - vocab
    if not_in_vocab:
        print("Not in vocab:")
        print(not_in_vocab)
    return list(words - not_in_vocab)

def main():
    # Get queries
    with open(args.words1) as f:
        words1 = f.read().splitlines()
    with open(args.words2) as f:
        words2 = f.read().splitlines()
    with open(args.queries) as f:
        queries = json.load(f)

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
    words1 = filter_words(words1, vocab)
    words2 = filter_words(words2, vocab)
    for k, v in queries.items():
        queries[k] = filter_words(v, vocab)

    print("Calculating similarity...")
    sims = get_cosines(words1, words2, queries, models)
    print(sims.head())

    print("Saving file...")
    sims.to_csv(args.output_file, index=False)


if __name__ == '__main__':
    main()


