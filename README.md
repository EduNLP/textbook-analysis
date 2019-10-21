# Textbook Analysis via Natural Language Processing
Code for the paper "Content Analysis of Textbooks via Natural Language Processing".
> Lucy*, L., Demszky*, D., Bromley, P. & Jurafsky, D. (2019). Content Analysis of Textbooks via Natural Language Processing: Novel Findings on Gender, Race, and Ethnicity in Texas US HistoryTextbooks. _In Preparation_.  *indicates equal contribution

This script is for those who would like to perform analyses on their own textbook data (or any other data), to better understand the representation of minorities and women in text. These scripts should be very easy to use, so you **do not need any technical background** to run these analyses. See our paper for a more detailed description of each method.

First, download this repository by running the following in the Terminal:

`git clone https://github.com/ddemszky/textbook-analysis.git`

Then, go into the directory:

`cd textbook-analysis`

Create and activate virtual environment:

`virtualenv env`
`source env/bin/activate`

Install all required packages:

`pip install -r requirements.txt`


## Data Format

First, prepare your data such that each textbook is in a separate text file (simple `.txt`), in the same directory. Perform any clean-ups that you think might be necessary (e.g. removing characters that you do not want, remove short lines, etc.).

# Counting the Mentions of People

## Pre-processing (TODO: @dora)

In order to count the number of times people are mentioned, it's important to first run co-reference resolution on the data so that pronouns, for example, are substituted by the nouns that they refer to. 

> todo: add a single line script to run coref, args: input directory (for all txt files), output directory (for all txt files)

## Counting the Mentions of Demographic Groups (TODO: @lucy)

To count the frequency of mentions for different groups of people (e.g. men vs women), run the following:

> todo: add a single line script, args: input directory, output directory, people_terms file

We include a `people_terms` file in `people_terms.csv`, but you can replace it with your own file. The format of this file should be the following: it should have 2 columns separated by a comma, the first including a word / phrase referring to people (lowercase) and the second should be the demographic group that the word / phrase belongs to. If a word belongs to multiple demographic groups, then add that as a separate line. For example:

> maid,woman
> african american,african american
> latina,latinx
> latina,woman

@lucy: can you make the above script run for bigrams?

An output file `people_mentions.csv` will be generated in the output directory. The file will have the following columns: 

* `source_text`: The name of the text file (corresponding to a textbook, for example). 
* `demographic`: The demographic category. 
* `count`: The number of terms belonging to that demographic in the given source text.

## Counting the Mentions of Named People (TODO: @lucy)

To count the frequency of mentions for named people (e.g. Eleanor Roosevelt), you first need to run Named Entity Recognition (NER). The following script will run NER on your files and it will also combine last names with the most recent full name in the data: 

> todo: add a single line script, args: input directory, output directory

This script will generate separate files for each textbook in the specified output directory, with counts of each named individual.

If you would also like to obtain demographic information for the named individuals automatically, you can run the following script. This script builds on Wikidata, which has a lot of missing information (e.g. it usually doesn't specify race for white people), but it has high coverage of gender information, for example. The `input_file` should be a list of named individuals, separated by newlines (@lucy: should it be full names, with middle names, or can you standardize automatically?). The argument `demographic_categories` should be a list of categories that you are interested in. The available categories are: `gender`, `ethnicity`, `occupation` (@lucy?).

> todo: add a single line script, args: input file, output file demographic categories

The output file will be a `.csv`, where the first colum is the name of the person and the rest of the columns correspond to each of the demographic categories specified. If the person was not found in the database, or the category was not listed, the value will be empty.

# Looking at How People Are Described

## Verbs and Adjectives (TODO: @lucy)
One way to understand how people are described is to look at the verbs and adjectives that they co-occur with. For this, you first need to run dependency parsing. You can run the following script, where the format of the `people_terms` file should be the way it is described above.

> todo: single line script, args: input directory, output_directoy, people_terms file

This script will output `people_descriptors.csv` in the output directory, with the following columns:

* `source_text`: The name of the text file (corresponding to a textbook, for example). 
* `people_term`: The specific people term.
* `demographic`: The demographic category. 
* `word`: The verb / adjective.
* `count`: The frequency of the particular word occurring with the particular people term (if a verb, this is counted separately for SUBJ and OBJ).
* `POS`: The part of speech tag for the word (ADJ or VERB).
* `relation`: If the word is a verb, indicate whether the people term is the subject of the verb (SUBJ) or the object of the verb (OBJ).

## Log odds ratio (TODO: @lucy)

We can look at which words are significantly more associated with one group vs another group based on word counts. (todo: add citation)

> todo: add one line script that calculates log odds based on a file that has word counts for the two groups

## Power, Agency and Sentiment (TODO: @lucy)

To estimate the association between groups and (todo: add more text). 

> todo: explain how to download NRC and add single line script that processes it

> todo:  explain how to download Connotation Frames and add single line script that processes it

> todo: single line script, args: people_descriptors file (generated above), connotation frames dict, nrc dict (it can be just one, too), output file

The script outputs a csv file in the output directory, called `power_agency_sentiment.csv`, with the following columns:

* `source_text`: The name of the text file (corresponding to a textbook, for example).
* `demographic`: The demographic category. 
* `dimension`: Name of the dimension.
* `score`: Score for the particular dimension.


## Measure Association Between Words (TODO: @dora)
Another way to measure association between words is to represent words as vectors and look at their distance in the vector space. For this, you first need to create vectors for the words in your text. You can do so by running the following script (note that this will take a while, depending on your data size and number of runs you want to do). 

> todo: single line script, args: input text file, output directory, number of runs, (add other args potentially)

This script will create model files ...

Get most closely associated word with a particular group.

> todo: single line script, args: model dir, list of words

Get similarity between two sets of words:

> todo: single line script, args: model dir, 1st list of words, 2nd list of words

# Analyzing Topics (TODO: @dora)

To induce topics in your data, you first need to run a topic model. Our script runs LDA, using the very efficient MALLET package. In order to run this, you first need to download MALLET, by running the following command:

> todo: add mallett download script

The following script runs the topic model:

> todo: add topic modeling script, that also calculates the prominence of each topic

You can inspect the resulting topics by looking at the following files: . 

## Topic Prominence

You can also look at their prominence in the following files:.

## Diversity of Topics Associated with a Group

To measure the association between groups and particular topics, run:

> todo: add script, args: topic words file, words indicating groups









