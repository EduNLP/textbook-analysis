# Textbook Analysis via Natural Language Processing
Code for the paper "Content Analysis of Textbooks via Natural Language Processing".
> Lucy*, L., Demszky*, D., Bromley, P. & Jurafsky, D. (2019). Content Analysis of Textbooks via Natural Language Processing: Novel Findings on Gender, Race, and Ethnicity in Texas US HistoryTextbooks. _In Preparation_.  *indicates equal contribution

This script is for those who would like to perform analyses on their own textbook data (or any other data), to better understand the representation of minorities and women in text. These scripts should be very easy to use, so you **do not need any technical background** to run these analyses. See our paper for a more detailed description of each method.

First, download this repository by running the following in the Terminal:

`git clone https://github.com/ddemszky/textbook-analysis.git`


# Data Format

First, prepare your data such that each textbook is in a separate text file (simple `.txt`), in the same directory. Perform any clean-ups that you think might be necessary (e.g. removing characters that you do not want, or remove lines that are short).

# Counting the mentions of people

## Pre-processing (@dora)

In order to count the number of times people are mentioned, it's important to first run co-reference resolution on the data so that pronouns, for example, are substituted by the nouns that they refer to. 

> todo: add a single line script to run coref, args: input directory (for all txt files), output directory (for all txt files)

## Counting the mentions of groups, separated by demographic (@lucy)

To count the frequency of mentions for different groups of people (e.g. men vs women), run the following:

> todo: add a single line script, args: input directory, output directory, people_terms file

We include a `people_terms` file in `people_terms.csv`, but you can replace it with your own file. The format of this file should be the following: it should have 2 columns separated by a comma, the first including a word / phrase referring to people (lowercase) and the second should be the demographic group that the word / phrase belongs to. If a word belongs to multiple demographic groups, then add that as a separate line. For example:

> maid,woman
> african american,african american
> latina,latinx
> latina,woman

An output file `people_mentions.csv` will be generated in the output directory. The file will have the following columns: 

* `source_text`: The name of the text file (corresponding to a textbook, for example). 
* `demographic`: The demographic category. 
* `count`: The number of terms belonging to that demographic in the given source text.


# Looking at how people are described

# Measuring topic prominence and their associations with people




