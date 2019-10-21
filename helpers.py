#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Dora Demszky (ddemszky@stanford.edu) and Lucy Li (lucy3_li@berkeley.edu)
import codecs
import glob
import string
from nltk.corpus import stopwords
import nltk
import re
from gensim.models import KeyedVectors

stopwords = set(stopwords.words('english')) | {'could', 'should', 'would', 'shall', 'must', 'may', 'many', 'most'}
punct_chars = list((set(string.punctuation) | {'»', '–', '—', '-',"­", '\xad', '-', '◾', '®', '©','✓','▲', '◄','▼','►', '~', '|', '“', '”', '…', "'", "`", '_', '•', '*', '■'} - {"'"}))
punct_chars.sort()
punctuation = ''.join(punct_chars)
replace = re.compile('[%s]' % re.escape(punctuation))
sno = nltk.stem.SnowballStemmer('english')
printable = set(string.printable)


def clean_text(text, remove_stopwords=True, remove_numeric=True, stem=False, remove_short=True):
    # lower case
    text = text.lower()
    # eliminate urls
    text = re.sub(r'http\S*|\S*\.com\S*|\S*www\S*', ' ', text)
    # substitute all other punctuation with whitespace
    text = replace.sub(' ', text)
    # replace all whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # strip off spaces on either end
    text = text.strip()
    # make sure all chars are printable
    text = ''.join([c for c in text if c in printable])
    words = text.split()
    if remove_stopwords:
        words = [w for w in words if w not in stopwords]
    if remove_numeric:
        words = [w for w in words if not w.isdigit()]
    if stem:
        words = [sno.stem(w) for w in words]
    if remove_short:
        words = [w for w in words if len(w) >= 3]
    return words

def get_book_txts(path, splitlines=False):
    print('Getting books...')
    bookfiles = [f for f in glob.glob(path + '/*.txt')]
    books = {}
    for f in bookfiles:
        txt = codecs.open(f, 'r', encoding='utf-8').read()
        if splitlines:
            txt = txt.splitlines()
        title = f.split('/')[-1]
        books[title] = txt
        print(title)
    return books

def get_models(filelist):
    model_files = [f for f in filelist if f.endswith('.wv')]
    models = [KeyedVectors.load(fname, mmap='r') for fname in model_files]
    return models