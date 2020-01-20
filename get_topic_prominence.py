#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
import gensim.corpora as corpora
from gensim.models.wrappers import LdaMallet
from gensim.models import CoherenceModel
from helpers import *
import pandas as pd
import json

parser = argparse.ArgumentParser()

parser.add_argument('--model_dir', required=True, help="Directory containing the topic model files.")
parser.add_argument('--num_topics', default=300, type=int, help="Number of topics to induce.")

args = parser.parse_args()




def main():
    print("Loading book boundaries...")
    books = json.loads(open(args.model_dir + '/book_start_end.json', 'r').read())

    print("Loading model...")
    model_path = args.model_dir + '/' + str(args.num_topics)
    model = LdaMallet.load(model_path)
    id2word = model.id2word
    word2id = {v: k for k, v in id2word.items()}
    word_topics = model.word_topics

    print("Getting topics for all books...")
    all_topics = pd.read_csv(model_path + 'doctopics.txt', sep='\t', header=0, index_col=0,
                             names=['docno'] + list(range(args.num_topics)))



if __name__ == '__main__':
    main()




