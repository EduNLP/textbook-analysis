#!/bin/bash

BIN_DIR=$1
DIRECTORY=$2
TOPICS=$3
echo "Data directory is" $DIRECTORY
echo "Number of topics is" $TOPICS

cd $DIRECTORY

$BIN_DIR/mallet import-file --input $DIRECTORY/data.input --output $DIRECTORY/data.mallet --keep-sequence --token-regex '\w+'
$BIN_DIR/mallet train-topics --input $DIRECTORY/data.mallet \
      --num-topics $TOPICS --output-state $DIRECTORY/topic-state.gz \
      --output-doc-topics $DIRECTORY/doc-topics.gz \
      --output-topic-keys $DIRECTORY/topic-words.gz --num-top-words 500 \
      --num-iterations 1000