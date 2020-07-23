#!/usr/local/bin/python
from collections import defaultdict
import math
import argparse


# Dan Jurafsky March 22 2013
# bayes.py
# Computes the "weighted log-odds-ratio, informative dirichlet prior" algorithm for 
# from page 388 of 
# Monroe, Colaresi, and Quinn. 2009. "Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict"

# assumes all 3 input files are space-separated, two columns, frequency followed by word
#1371056 the
#923839 and
#765263 i

def myswap(inlist):
    return [inlist[1],int(inlist[0])]

parser = argparse.ArgumentParser(description='Computes the weighted log-odds-ratio, informative dirichlet prior algorithm')
parser.add_argument('-f','--first', help='Description for first counts file ', default='greatreviews.out')
parser.add_argument('-s','--second', help='Description for second counts file', default='badreviews.out')
parser.add_argument('-p','--prior', help='Description for prior counts file', default='allreviewwords.out')
args = vars(parser.parse_args())

counts1 = defaultdict(int,[myswap(line.strip().split(' ')) for line in open(args['first'])])
counts2 = defaultdict(int,[myswap(line.strip().split(' ')) for line in open(args['second'])])
prior = defaultdict(int,[myswap(line.strip().split(' ')) for line in open(args['prior'])])
sigmasquared = defaultdict(float)
sigma = defaultdict(float)
delta = defaultdict(float)

for word in prior.keys():
    prior[word] = int(prior[word] + 0.5)

for word in counts2.keys():
    counts1[word] = int(counts1[word] + 0.5)
    if prior[word] == 0:
        prior[word] = 1

for word in counts1.keys():
    counts2[word] = int(counts2[word] + 0.5)
    if prior[word] == 0:
        prior[word] = 1

n1  = sum(counts1.values())
n2  = sum(counts2.values())
nprior = sum(prior.values())


for word in prior.keys():
    #if prior[word] == 0 and (counts2[word] > 10):
        #prior[word] = 1
    if prior[word] > 0:
        l1 = float(counts1[word] + prior[word]) / (( n1 + nprior ) - (counts1[word] + prior[word]))
        l2 = float(counts2[word] + prior[word]) / (( n2 + nprior ) - (counts2[word] + prior[word]))
        sigmasquared[word] =  1/(float(counts1[word]) + float(prior[word])) + 1/(float(counts2[word]) + float(prior[word]))
        sigma[word] =  math.sqrt(sigmasquared[word])
        delta[word] = ( math.log(l1) - math.log(l2) ) / sigma[word]

for word in sorted(delta, key=delta.get):
    print(word, "%.3f" % delta[word])