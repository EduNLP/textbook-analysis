"""
Calculates average NRC VAD and connotation frames 
scores for different categories of people. 
"""
import argparse
import csv
from nltk.stem.wordnet import WordNetLemmatizer
from collections import defaultdict, Counter
import pandas as pd
from scipy.stats import zscore
import math
import warnings
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

parser = argparse.ArgumentParser()

parser.add_argument('--input_file', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--inspect', default=False)
parser.add_argument('--category')
parser.add_argument('--score_type')

args = parser.parse_args()

if args.inspect and (args.category is None or args.score_type is None):
    parser.error("--inspect requires --category and --score_type.")

def get_ap_lexicon(): 
    '''
    @output: 
    - Two dictionaries of format {word : annotation}
    '''
    lexicon = './wordlists/agency_power.csv'
    agencies = {}
    powers = {}
    with open(lexicon, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            word = WordNetLemmatizer().lemmatize(row['verb'], 'v')
            if row['agency'] == 'agency_pos': 
                agencies[word] = 1
            elif row['agency'] == 'agency_neg': 
                agencies[word] = -1
            else: 
                agencies[word] = 0
            if row['power'] == 'power_agent': 
                powers[word] = 1
            elif row['power'] == 'power_theme': 
                powers[word] = -1
            else: 
                powers[word] = 0
    return (agencies, powers)

def get_NRC_lexicon(): 
    '''
    @output: 
    - A dictionary of format {word : score}
    '''
    lexicon = './wordlists/NRC-VAD-Lexicon.txt'
    val_dict = {}
    aro_dict = {}
    dom_dict = {}
    with open(lexicon, 'r') as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            word = row['Word']
            val_dict[word] = float(row['Valence'])
            aro_dict[word] = float(row['Arousal'])
            dom_dict[word] = float(row['Dominance'])
    return (val_dict, aro_dict, dom_dict)

def get_conn_lexicon(): 
    '''
    @output: 
    - A dictionary of format {measurement : {word : score}}
    '''
    lexicon = './wordlists/full_frame_info.txt'
    ret = defaultdict(dict)
    vocab = set()
    with open(lexicon, 'r') as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            vocab.add(row['verb'])
            for key in row: 
                if key != 'verb':
                    ret[key][row['verb']] = float(row[key])
    return (ret, vocab)

def calculate_scores(agencies, powers, val_dict, aro_dict, \
        dom_dict, conn_lexicon, conn_vocab): 
    '''
    The outputs of this function are dictionaries that are formatted
    in a way so that they can be easily transformed into pandas dataframes
    if needed. 
    '''
    agen_d = {'Category' : [], 'Value': [], 'Word' : []}
    power_d = {'Category' : [], 'Value': [], 'Word' : []}
    adj = {'Category' : [], 'Measurement' : [], 'Value' : [], 'Word' : []}
    sent_d = {'Category' : [], 'Value': [], 'Word' : []}
    with open(args.input_file, 'r') as infile: 
        reader = csv.DictReader(infile)
        for row in reader: 
            ID = row['token_ID']
            title = row['filename']
            category = row['category']
            word = row['word']
            pos = row['POS']
            relation = row['rel']
            if pos == 'VERB' and relation == 'nsubj':
                # Connotation frames
                word = WordNetLemmatizer().lemmatize(word, 'v')
                if word in powers: 
                    power_d['Value'].append(powers[word])
                    power_d['Category'].append(category)
                    power_d['Word'].append(word)
                if word in agencies: 
                    agen_d['Value'].append(agencies[word])
                    agen_d['Category'].append(category)
                    agen_d['Word'].append(word)
                if word in conn_vocab: 
                    sent_d['Category'].append(category)
                    sent_d['Value'].append(conn_lexicon['Perspective(ws)'][word])
                    sent_d['Word'].append(word)
            elif relation == 'dobj':
                # Connotation frames
                word = WordNetLemmatizer().lemmatize(word, 'v')
                if word in powers: 
                    power_d['Value'].append(-powers[word])
                    power_d['Category'].append(category)
                    power_d['Word'].append(word)
                if word in conn_vocab: 
                    sent_d['Category'].append(category)
                    sent_d['Value'].append(conn_lexicon['Perspective(wo)'][word])
                    sent_d['Word'].append(word)
            elif (pos == 'ADJ' and relation == 'nsubj') or (relation == 'amod'):
                # NRC VAD
                if word in val_dict: 
                    val = val_dict[word]
                    aro = aro_dict[word]
                    dom = dom_dict[word]
                    adj['Category'].append(category)
                    adj['Measurement'].append('Valence')
                    adj['Value'].append(val)
                    adj['Word'].append(word)
                    adj['Category'].append(category)
                    adj['Measurement'].append('Arousal')
                    adj['Value'].append(aro)
                    adj['Word'].append(word)
                    adj['Category'].append(category)
                    adj['Measurement'].append('Dominance')
                    adj['Value'].append(dom)
                    adj['Word'].append(word)
    return power_d, agen_d, sent_d, adj

def look_at_examples(d, category, score_dict, top_n=30): 
    '''
    Takes in a category of people and prints out the
    most common words 

    For example, you can run this function with the following:
    d = agen_d
    category = 'black'
    score_dict = agencies 
    And it will print out the most common verbs associated
    with black people in the text and those verbs' agency scores. 

    Example usage: 
    python get_lexicon_averages.py --input_file results/people_descriptors.csv 
        --output_dir results/ --inspect True --category black --score_type agency
    '''
    df = pd.DataFrame.from_dict(d)
    category_df = df[df['Category'] == category]
    counts_words = Counter(category_df['Word'].tolist())
    for w in counts_words.most_common(top_n): 
        print(w, score_dict[w[0]])

def write_output(writer, df, label): 
    df.loc[:,'value'] = zscore(df['Value'])
    df = df.drop(columns=['Value'])
    stats = df.groupby(['Category']).agg(['mean', 'count', 'std'])
    cis = []
    for i in stats.index:
        m, c, s = stats.loc[i]
        cis.append(1.96*s/math.sqrt(c))
    stats['ci'] = cis
    for index, row in stats.iterrows():
        writer.writerow({'category': row.name,
                    'dimension': label, 
                    'mean':row['value']['mean'], 
                    "ci": row['ci'].values[0]})

def main():
    agencies, powers = get_ap_lexicon()
    val_dict, aro_dict, dom_dict = get_NRC_lexicon()
    conn_lexicon, conn_vocab = get_conn_lexicon()
    power_d, agen_d, sent_d, adj = calculate_scores(agencies, powers, val_dict, aro_dict, \
        dom_dict, conn_lexicon, conn_vocab)
    if not args.inspect: 
        power_df = pd.DataFrame.from_dict(power_d)
        agen_df = pd.DataFrame.from_dict(agen_d)
        sent_df = pd.DataFrame.from_dict(sent_d)
        adj_df = pd.DataFrame.from_dict(adj)
        val_df = adj_df[adj_df['Measurement'] == 'Valence']
        aro_df = adj_df[adj_df['Measurement'] == 'Arousal']
        dom_df = adj_df[adj_df['Measurement'] == 'Dominance']
        with open(args.output_dir + 'lexicon_output.csv', 'w') as outfile:
            fieldnames = ['category', 'dimension', 'mean', 'ci']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            write_output(writer, power_df, 'power')
            write_output(writer, agen_df, 'agency')
            write_output(writer, sent_df, 'sentiment')
            write_output(writer, val_df, 'valence')
            write_output(writer, aro_df, 'arousal')
            write_output(writer, dom_df, 'dominance')
    else: 
        if args.score_type == 'agency':
            look_at_examples(agen_d, args.category, agencies)
        elif args.score_type == 'power':
            look_at_examples(power_d, args.category, powers)
        elif args.score_type == 'sentiment':
            look_at_examples(sent_d, args.category, conn_lexicon['Perspective(ws)'])
            look_at_examples(sent_d, args.category, conn_lexicon['Perspective(wo)'])
        elif args.score_type == 'valence':
            look_at_examples(adj, args.category, val_dict)
        elif args.score_type == 'arousal':
            look_at_examples(adj, args.category, aro_dict)
        elif args.score_type == 'dominance':
            look_at_examples(adj, args.category, dom_dict)
        else: 
            print("Invalid score type.")

if __name__ == '__main__':
    main()
