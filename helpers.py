#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import glob

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