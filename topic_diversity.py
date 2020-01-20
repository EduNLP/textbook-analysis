#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
import json
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--topic_dir', required=True, help="Directory containing the topic model files.")
parser.add_argument('--words', required=True, help="Comma-separated list of words (unigrams and bigrams)"
                                                   "associated with a particular group.")
parser.add_argument('--title', required=False, help="Title of the book to perform the analysis on.")
parser.add_argument('--all_books', action='store_true', help="Whether to perform analyses across all books.")

args = parser.parse_args()

def get_topics_for_word(words, topic_names):
    topic_ids = set()
    for k, v in topic_names.items():
        if any([w in v for w in words]):
            topic_ids.add(k)
    for t in topic_ids:
        print("%s %s" % (t, topic_names[t]))
    return topic_ids


def main():
    topic_names = json.load(open('%s/topic_names.json' % args.topic_dir, 'r'))
    print("Analyzing words: %s" % args.words)
    dir = None
    if args.all_books:
        dir = args.topic_dir
    elif not args.title:
        print("If you don't set --all_books, then you must specify a book title.")
    else:
        dir = "%s/%s" % (args.topic_dir, args.title)
    topic_ids = get_topics_for_word(args.words.split(","), topic_names)
    pmi = np.load(dir + '/pmi.npy')
    val = np.mean([pmi[int(i),int(j)] for j in topic_ids for i in topic_ids if j != i])
    print("Score for group: %.3f" % val)




if __name__ == '__main__':
    main()