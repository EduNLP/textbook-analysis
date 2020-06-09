"""
Calculate log odds for two groups of descriptors. 
"""

import os
import json
from collections import defaultdict, Counter
import helpers
import string
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input_file', required=True)
parser.add_argument('--output_dir', required=True)
parser.add_argument('--group1', required=True)
parser.add_argument('--group2', required=True)

args = parser.parse_args()

group1 = args.group1.split(',')
group2 = args.group2.split(',')

def write_out_log_odds():
    translator = str.maketrans('', '', string.punctuation)
    marked = set() # word IDs associated with group 1
    all_count = Counter() # {(id, word) : count}
    group1_count = Counter()
    group2_count = Counter()
    with open(args.input_file, 'r') as infile: 
        for line in infile:
            contents = line.strip().split(',')
            word = contents[4]
            proc_word = word.translate(translator)
            if proc_word == '': continue
            if contents[3] in group1: 
                group1_count[proc_word] += 1
                marked.add(contents[0] + contents[1])
    # we open the file twice to avoid overlap w/ group 1
    with open(args.input_file, 'r') as infile: 
        for line in infile:
            contents = line.strip().split(',')
            word = contents[4]
            proc_word = word.translate(translator)
            if proc_word == '': continue
            if contents[3] in group2 and (contents[0] + contents[1]) not in marked: 
                group2_count[word] += 1
            all_count[word] += 1

    with open(os.path.join(args.output_dir, 'group1_counts.txt'), 'w') as outfile: 
        for word in all_count: 
            outfile.write(str(group1_count[word]) + ' ' + word + '\n')
    with open(os.path.join(args.output_dir, 'group2_counts.txt'), 'w') as outfile: 
        for word in all_count: 
            outfile.write(str(group2_count[word]) + ' ' + word + '\n')
    with open(os.path.join(args.output_dir, 'all_counts.txt'), 'w') as outfile: 
        for word in all_count: 
            outfile.write(str(all_count[word]) + ' ' + word + '\n')

def descriptor_log_odds(): 
    '''
    Runs log odds on people descriptors, which
    is the output of main_people_descriptors().
    '''
    os.system('python ./bayesequal.py -f ' + os.path.join(args.output_dir, 'group1_counts.txt') + \
        ' -s ' + os.path.join(args.output_dir, 'group2_counts.txt') + \
        ' -p ' + os.path.join(args.output_dir, 'all_counts.txt') + ' > ' + \
        os.path.join(args.output_dir, 'log_odds.txt'))

def main(): 
	write_out_log_odds()                                     
	descriptor_log_odds()

if __name__ == '__main__':
    main()