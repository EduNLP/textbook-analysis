#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Dora Demszky (ddemszky@stanford.edu) and Lucy Li (lucy3_li@berkeley.edu)
import codecs
import glob
import string
import nltk
import re
from gensim.models import KeyedVectors
import seaborn as sns

stopwords = open("wordlists/stopwords/en/mallet.txt", "r").read().splitlines()
punct_chars = list((set(string.punctuation) | {'»', '–', '—', '-',"­", '\xad', '-', '◾', '®', '©','✓','▲', '◄','▼','►', '~', '|', '“', '”', '…', "'", "`", '_', '•', '*', '■'} - {"'"}))
punct_chars.sort()
punctuation = ''.join(punct_chars)
replace = re.compile('[%s]' % re.escape(punctuation))
sno = nltk.stem.SnowballStemmer('english')
printable = set(string.printable)

def split_terms_into_sets(people_terms_path): 
    '''
    If the third column of the input file is "unmarked" then the word is unmarked
    '''
    possible_marks = set() 
    not_marks = set() # everything else
    with open(people_terms_path, 'r') as infile: 
        for line in infile: 
            contents = line.strip().split(',')
            if contents[2] == 'unmarked': 
                not_marks.add(contents[0].lower())
            else: 
                possible_marks.add(contents[0].lower())
    return possible_marks, not_marks

def get_word_to_category(people_terms_path): 
    word2dem = {}
    with open(people_terms_path, 'r') as infile: 
        for line in infile: 
            contents = line.strip().split(',')
            word2dem[contents[0]] = contents[1]
    return word2dem

def clean_text(text,
               remove_stopwords=True,
               remove_numeric=True,
               stem=False,
               remove_short=True):
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
    bookfiles = sorted([f for f in glob.glob(path + '/*.txt')])
    books = {}
    for f in bookfiles:
        txt = codecs.open(f, 'r', encoding='utf-8').read()
        if splitlines:
            txt = txt.splitlines()
        title = f.split('/')[-1].split(".")[0]
        books[title] = txt
        print(title)
    return books

def get_models(filelist):
    model_files = [f for f in filelist if f.endswith('.wv')]
    models = [KeyedVectors.load(fname, mmap='r') for fname in model_files]
    return models

title_abbreviations = {
    "America_A_Narrative_History_WWNorton_10th": "Am. Narr. Hist., W.W.N.",
    "America_Past_And_Present_Pearson_10th": "Am. Past & Present, Pearson",
    "american_history_connecting_with_the_past": "Am. Hist. Conn. w/ Past, M.H.",
    "Americas_History_Bedford_8th": "Am. Hist., Bedford",
    "by_the_people": "By The People, Pearson",
    "Give_Me_Liberty_An_American_History_WWNorton_3rd": "Give Me Liberty, W.W.N.",
    "history_alive_united_states_thru_industrialism": "Hist. Alive!, TCI",
    "hmh_the_americans_us_history_since_1877": "US. Hist. Since 1877: HMH",
    "mastering_the_teks": "Mastering the TEKS, Jarret",
    "pearson_us_history": "US Hist., Pearson",
    "teks_us_history": "TEKS US Hist., M. H.",
    "The_American_Pageant_Cengage_14th": "The Am. Pageant, Cengage",
    "The_Unfinished_Nation_A_Concise_History_of_the_American_People_McGraw-Hill_8th": "The Unfinished Nation, M.H.",
    "us_history_early_colonial_period_through_reconstruction": "US. Hist. Through Reconstr., HMH",
    "Visions_of_America_A_History_of_the_United_States_Pearson_2nd": "Visions of Am., Pearson"
}

# state adopted ones are triangular
shape_mapper = {
    "America_A_Narrative_History_WWNorton_10th": "o",
    "America_Past_And_Present_Pearson_10th": "8",
    "american_history_connecting_with_the_past": "H",
    "Americas_History_Bedford_8th": "p",
    "by_the_people": "X",
    "Give_Me_Liberty_An_American_History_WWNorton_3rd": "s",
    "history_alive_united_states_thru_industrialism": "*",
    "hmh_the_americans_us_history_since_1877": ">",
    "mastering_the_teks": "P",
    "pearson_us_history": "v",
    "teks_us_history": "^",
    "The_American_Pageant_Cengage_14th": "D",
    "The_Unfinished_Nation_A_Concise_History_of_the_American_People_McGraw-Hill_8th": "d",
    "us_history_early_colonial_period_through_reconstruction": "<",
    "Visions_of_America_A_History_of_the_United_States_Pearson_2nd": "h"
}

state_adopted_map = {
    'by_the_people' : 'no',
    'american_history_connecting_with_the_past' : 'no',
    'teks_us_history' : 'yes',
    'hmh_the_americans_us_history_since_1877' : 'yes',
    'The_Unfinished_Nation_A_Concise_History_of_the_American_People_McGraw-Hill_8th': 'no',
    'Give_Me_Liberty_An_American_History_WWNorton_3rd': 'no',
    'The_American_Pageant_Cengage_14th': 'no',
    'us_history_early_colonial_period_through_reconstruction' : 'yes',
    'Americas_History_Bedford_8th' : 'no',
    'history_alive_united_states_thru_industrialism' : 'no',
    'Visions_of_America_A_History_of_the_United_States_Pearson_2nd' : 'no',
    'pearson_us_history': 'yes',
    'America_A_Narrative_History_WWNorton_10th' : 'no',
    'America_Past_And_Present_Pearson_10th': 'no',
    'mastering_the_teks': 'no',
}

def get_title_abbr():
    return title_abbreviations

def get_shapes(abbr=True):
    if abbr:
        return {title_abbreviations[t]: s for t, s in shape_mapper.items()}
    return shape_mapper

def get_colors(abbr=False):
    colors = sns.color_palette("Set1", n_colors=15, desat=.5)
    if abbr:
        return {title_abbreviations[t]: colors[i] for i, t in enumerate(shape_mapper)}
    return {t: colors[i] for i, t in enumerate(shape_mapper)}
