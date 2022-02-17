#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dora Demszky (ddemszky@stanford.edu), based on <cite: Chenhao>
import functools
import argparse
import json
import logging
from helpers import *
from nltk import *
import itertools
import numpy as np
from collections import Counter, defaultdict
import io

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', required=True, help="Directory of input text files.")
parser.add_argument("--output_dir",
                    help=("output directory for intermediate data"),
                    type=str)
parser.add_argument('--mallet_dir', required=True, help="Location of MALLET binary file.")
parser.add_argument('--num_topics', default=100, type=int, help="Number of topics to induce.")
parser.add_argument('--stem', action='store_true', help="Whether to stem words before running the topic model "
                                                        "(in the paper, we do).")

args = parser.parse_args()

def generate_cooccurrence_from_int_set(articles, num_topics=100):
    matrix = np.zeros((num_topics, num_topics))
    for topics in articles:
        for topic in topics:
            matrix[topic, topic] += 1
        for (i, j) in itertools.combinations(topics, 2):
            matrix[i, j] += 1
            matrix[j, i] += 1
    return matrix

def find_bigrams(sentences, output_file, threshold=100, min_count=5):
    unigram_count = get_word_count(sentences, ngrams=1, words_func=get_ngram_list)
    total_words = float(sum(unigram_count.values()))
    bigram_count = get_word_count(sentences, ngrams=2, words_func=get_ngram_list)

    bigram_list = []
    for w in bigram_count:
        words = w.split()
        score = (bigram_count[w] - min_count) * total_words \
                / (unigram_count[words[0]] * unigram_count[words[1]])
        if score > threshold:
            bigram_list.append((score, w))
    bigram_list.sort(reverse=True)
    with open(output_file, "w") as fout:
        for score, w in bigram_list:
            fout.write("%s\n" % json.dumps({"word": w, "score": score}))


def get_ngram_list(input_words, ngrams=1, bigram_dict=None):
    words = [w.lower() for w in input_words.split()]
    result = []
    for start in range(len(words) - ngrams + 1):
        tmp_words = words[start:start + ngrams]
        w = " ".join(tmp_words)
        result.append(w)
    return result


def get_mixed_tokens(input_words, ngrams=1, bigram_dict=None):
    words = [w.lower() for w in input_words.split()]
    result, index = [], 0
    while index < len(words):
        w = words[index]
        # look forward
        if index < len(words) - 1:
            bigram = w + " " + words[index + 1]
            if bigram in bigram_dict:
                result.append(bigram)
                index += 2
                continue
        result.append(w)
        index += 1
    return result


def get_word_count(sentences, ngrams=1, bigram_dict=None, words_func=None):
    result = defaultdict(int)
    for sent in sentences:
        words = words_func(sent, ngrams=ngrams, bigram_dict=bigram_dict)
        for w in words:
            result[w] += 1
    return result


def load_bigrams(filename):
    bigram_dict = {}
    with open(filename) as fin:
        for line in fin:
            data = json.loads(line)
            bigram_dict[data["word"]] = data["score"]
    return bigram_dict


def get_word_dict(word_count, top=10000, filter_regex=None):
    if filter_regex:
        word_count = {w: word_count[w] for w in word_count
                      if all([re.match(filter_regex, sw) for sw in w.split()])}
    words = get_most_frequent(word_count, top=top)
    return {v[1]: i for i, v in enumerate(words)}


def get_most_frequent(word_cnt, top=10000):
    words = [(word_cnt[w], w) for w in word_cnt
             if re.match("\w+", w)]
    words.sort(reverse=True)
    min_threshold = words[min(top, len(words)) - 1][0]
    return [v for v in words if v[0] >= min_threshold]


def write_word_dict(vocab_dict, word_count, filename):
    with io.open(filename, mode="w", encoding="utf-8") as fout:
        ids = sorted(vocab_dict.values())
        reverse_dict = {i: w for (w, i) in vocab_dict.items()}
        for wid in ids:
            fout.write("%d\t%s\t%d\n" % (wid, reverse_dict[wid],
                word_count[reverse_dict[wid]]))

def convert_word_count_mallet(word_dict, sentences, output_file,
                              words_func=None):
    doc_id = 0
    with open(output_file, "w") as fout:
        for sent in sentences:
            doc_id += 1
            words = Counter(words_func(sent))
            words = [(word_dict[w], words[w])
                     for w in words if w in word_dict]
            words.sort()
            word_cnts = [" ".join([str(wid)] * cnt) for (wid, cnt) in words]
            fout.write("%s %s\n" % (doc_id, " ".join(word_cnts)))

def get_mallet_input_from_words(sentences, data_dir, vocab_size=10000):
    bigram_file = "%s/bigram_phrases.txt" % data_dir
    find_bigrams(sentences, bigram_file)
    bigram_dict = load_bigrams(bigram_file)
    word_cnts = get_word_count(sentences, bigram_dict=bigram_dict, words_func=get_mixed_tokens)
    vocab_dict = get_word_dict(word_cnts, top=vocab_size, filter_regex="\w\w+")
    write_word_dict(vocab_dict, word_cnts,
                          "%s/data.word_id.dict" % data_dir)
    convert_word_count_mallet(vocab_dict, sentences,
                              "%s/data.input" % data_dir,
                              words_func=functools.partial(
                                  get_mixed_tokens,
                                  bigram_dict=bigram_dict))

def read_word_dict(filename, vocab_size=-1):
    vocab_map = {}
    with io.open(filename, "r", encoding="utf-8") as fin:
        count = 0
        for line in fin:
            count += 1
            if vocab_size > 0 and count > vocab_size:
                break
            try:
                wid, word, _ = line.strip().split("\t")
                vocab_map[int(wid)] = word
            except:
                print(line)
    return vocab_map

def load_topic_words(vocab, input_file, top=10):
    """Get the top 10 words for each topic"""
    topic_map = {}
    with open(input_file) as fin:
        for line in fin:
            parts = line.strip().split()
            tid = int(parts[0])
            top_words = parts[2:2+top]
            topic_map[tid] = ",".join([vocab[int(w)] for w in top_words])
    return topic_map


def load_doc_topics(sentences, doc_topic_file, threshold):
    """Load topics in each document"""
    articles = []
    with open(doc_topic_file) as tfin:
        for _ in sentences:
            topic_line = tfin.readline()
            if not topic_line:
                break
            topics = topic_line.strip().split()[2:]
            topics = set([i for (i, v) in enumerate(topics)
                         if float(v) > threshold])
            articles.append(topics)
    return articles

def load_articles(sentences, topic_dir, threshold):
    vocab_file = "%s/data.word_id.dict" % topic_dir
    doc_topic_file = "%s/doc-topics.gz" % topic_dir
    topic_word_file = "%s/topic-words.gz" % topic_dir
    vocab = read_word_dict(vocab_file)
    topic_map = load_topic_words(vocab, topic_word_file)
    articles = load_doc_topics(sentences, doc_topic_file, threshold=threshold)
    return articles, vocab, topic_map

def get_count_cooccur(articles, func=generate_cooccurrence_from_int_set):
    cooccur = func(articles)
    count = np.diag(cooccur).copy()
    np.fill_diagonal(cooccur, 0)
    return {"count": count, "cooccur": cooccur,
            "articles": len(articles)}

def get_pmi(matrix, topic_count, total,
            num_topics=50,
            add_one=1.0):
    result = matrix.copy()
    for i in range(num_topics):
        for j in range(i + 1, num_topics):
            score = get_log_pmi(matrix[i, j],
                                      topic_count[i], topic_count[j], total,
                                      add_one=add_one)
            if np.isnan(score):
                score = 0
            result[i, j] = score
            result[j, i] = score
    print('pmi')
    print(result[:10, :10])
    return result

def get_log_pmi(xy, x, y, total, add_one=1.0):
    if add_one < 0:
        add_one = 0
    return np.log(xy + add_one) + np.log(total + add_one) \
            - np.log(x + add_one) - np.log(y + add_one)

def get_scores(articles, num_topics, output_dir,
                               cooccur_func=None):
    print('Counting co-occurrence...')
    result = get_count_cooccur(articles, func=cooccur_func)
    np.save('%s/cooccur.npy' %output_dir, result['cooccur'])
    np.save('%s/topic_count.npy' % output_dir, result['count'])
    print(result['cooccur'][:10, :10])
    print('Getting pmi...')
    # pmi is based on overall co-occurrences
    pmi = get_pmi(result["cooccur"], result["count"],
                  float(result["articles"]), num_topics=num_topics)
    np.save('%s/pmi.npy' % output_dir, pmi)
    return pmi


def main():
    print("Loading books...")
    books = get_book_txts(args.input_dir, splitlines=True)

    print('Combining data and cleaning data...')
    book_texts = {}
    for k, v in books.items():
        book_texts[k] = []
        for line in v:
            for sent in nltk.sent_tokenize(line):
                if len(sent) < 15:
                    continue
                book_texts[k].append(' '.join(clean_text(sent,
                                             stem=args.stem,
                                             remove_short=True,
                                             remove_stopwords=True)))

    titles = sorted(books.keys())
    all_text = []
    book2length = []
    for title in titles:
        texts = book_texts[title]
        book2length.append((title, len(texts)))
        for t in texts:
            all_text.append(t)


    output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(args.num_topics, "topics")
    num_topics = args.num_topics
    cooccur_func = functools.partial(generate_cooccurrence_from_int_set,
                                     num_topics=num_topics)


    # generate mallet topics
    get_mallet_input_from_words(all_text, output_dir)

    # run mallet to prepare topics inputs
    # users can also generate mallet-style topic inputs inputs
    logging.info("running mallet to get topics")
    if not os.path.exists(os.path.join(args.mallet_dir, 'mallet')):
        sys.exit("Error: Unable to find mallet at %s" % args.mallet_dir)
    os.system("./mallet.sh %s %s %d" % (args.mallet_dir,
                                        output_dir,
                                        num_topics))


    # load mallet outputs (threshold for keeping a topic = 0.1)
    articles, vocab, topic_names = load_articles(all_text, output_dir, threshold=.1)
    save_topic_names = '%s/topic_names.json' % output_dir
    with open(save_topic_names, 'w') as f:
        f.write(json.dumps(topic_names))

    print(topic_names)


    # compute strength between pairs and generate outputs
    get_scores(articles, num_topics, output_dir, cooccur_func=cooccur_func)

    print("Separating topics per book...")

    doc_topic_file = '%s/doc-topics.gz' % output_dir
    doc_topics = open(doc_topic_file).read().splitlines()
    print(len(doc_topics), 'articles total')
    prev = 0
    for (title, length) in book2length:
        book_output_dir = "%s/%s" % (output_dir, title)
        if not os.path.exists(book_output_dir):
            os.makedirs(book_output_dir)
        with open(book_output_dir + '/doc-topics.gz', 'w') as outf:
            outf.write('\n'.join(doc_topics[prev:prev + length]))

        get_scores(articles[prev:prev + length], num_topics, book_output_dir, cooccur_func)
        prev += length


if __name__ == "__main__":
    main()

