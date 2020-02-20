#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Dora Demszky (ddemszky@stanford.edu)
import argparse
from helpers import *
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', required=True, help="Directory of input text files.")
parser.add_argument("--output",
                    help=("Output file for word counts."),
                    type=str)
parser.add_argument('--stem', action='store_true', help="Whether to stem words.")

args = parser.parse_args()

def main():
    print("Loading books...")
    books = get_book_txts(args.input_dir, splitlines=False)

    all_text = []
    print("Counting words...")
    for k, v in books.items():
        print(k)
        all_text.extend(clean_text(v, stem=args.stem, remove_short=True, remove_stopwords=True))

    counts = Counter(all_text).most_common()
    with open(args.output, "w") as f:
        for w, c in counts:
            f.write("%s\t%d\n" % (w, c))

if __name__ == "__main__":
    main()

