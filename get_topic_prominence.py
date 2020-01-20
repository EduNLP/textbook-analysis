#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu)
import argparse
from helpers import *
import pandas as pd
import json
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--topic_dir', required=True, help="Directory containing the topic model files.")
parser.add_argument('--textbook_dir', required=True, help="Directory containing the textbook files.")

args = parser.parse_args()

def main():
    topic_names = json.load(open('%s/topic_names.json' % args.topic_dir, 'r'))
    books = get_book_txts(args.textbook_dir, splitlines=False)
    dicts = []

    for title, book in books.items():
        topic_counts = np.load('%s/%s/topic_count.npy' % (args.topic_dir, title))
        book_total = np.sum(topic_counts)
        for topic_id, topic_words in topic_names.items():
            topic_count = topic_counts[int(topic_id)]
            d = {"book": title,
                 "topic_id": topic_id,
                 "topic_words": topic_words,
                 "raw_count": int(topic_count),
                 "topic_proportion": topic_count / book_total
            }
            dicts.append(d)
    df = pd.DataFrame(dicts)
    df.to_csv('%s/topic_prominence.csv' % args.topic_dir, index=False)



if __name__ == '__main__':
    main()




