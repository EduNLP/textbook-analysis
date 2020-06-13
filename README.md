# Textbook Analysis via Natural Language Processing
Code for the paper "Content Analysis of Textbooks via Natural Language Processing".
> Lucy*, L., Demszky*, D., Bromley, P. & Jurafsky, D. (2019). Content Analysis of Textbooks via Natural Language Processing: Findings on Gender, Race, and Ethnicity in Texas US HistoryTextbooks. _Under Review_.  *indicates equal contribution

This script is for those who would like to perform analyses on their own textbook data (or any other data), to better understand the representation of minorities and women in text. You **do not need any technical background** to run these analyses. See our paper for a more detailed description of each method.

First, download this repository by running the following in the Terminal and then enter the directory:

```
git clone https://github.com/ddemszky/textbook-analysis.git
cd textbook-analysis
```

Create and activate virtual environment:

```
virtualenv -p python3 env
source env/bin/activate
```

Install all required packages:

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # install SpaCy models for English
```

Our scripts were written for the studies described in our paper. It's likely you might be researching other research questions about other groups of people. For example, if you were analyzing differences in the descriptors of politicians pre-1850 and post-1850, you could run the files in our toolkit using a list of people terms categorized based on that comparison. Email us if you want some advice for your specific use case. 

## Data Format

First, prepare your data such that each textbook is in a separate text file (simple `.txt`), in the same directory. Perform any clean-ups that you think might be necessary (e.g. removing characters that you do not want, remove short lines, etc.).

# Counting the Mentions of People

## Pre-processing

In order to count the number of times people are mentioned, it's important to first run co-reference resolution on the data so that pronouns, for example, are substituted by the nouns that they refer to. Run the script below, replacing the input and output directories with your paths.

```
python run_coref.py --input_dir data/source_txts --output_dir data/coref_resolved_txts
```

Note that this script may take a while to run on large files. It took ~1hr on our 15 textbooks, using my local machine.

## Counting the Mentions of Demographic Groups 

To count the frequency of mentions for different groups of people (e.g. different genders), run the following:

```
python count_mentions.py --input_dir data/coref_resolved_txts --output_dir results/ --people_terms wordlists/people_terms.csv
```

We include a `people_terms.csv` file in `wordlists`, but you can replace it with your own file. The format of this file should be the following: it should have 3 columns separated by a comma, the first including a word / phrase referring to people (lowercase), the second should be the demographic group that the word / phrase belongs to, and the third is the type of demographic. If a word belongs to multiple demographic groups, then add that as a separate line. For example:

> maid,woman,gender

> african,black,race/ethnicity

> latina,latinx,race/ethnicity

> latina,woman,gender

Our script takes unmarked terms, such as *farmer*, and if they are modified by a marker such as *black farmer*, recategorizes the instance of *farmer* to the category *black*. 

An output file `people_mentions.csv` will be generated in the output directory. The file will have the following columns: 

* `source_text`: The name of the text file (corresponding to a textbook, for example). 
* `demographic`: The demographic category. 
* `count`: The number of terms belonging to that demographic in the given source text.

The above script works for unigrams (single words), but not yet for bigrams (phrases). 

## Counting the Mentions of Named People 

To count the frequency of mentions for named people (e.g. Eleanor Roosevelt), you first need to run Named Entity Recognition (NER). The following script will run NER on your files and it will also combine last names with the most recent full name in the data. It will also output a new dataset in `ner_dir` where named entities have standardized Wikidata names, e.g. Franklin D. Roosevelt -> Franklin Delano Roosevelt. 

```
python count_names.py --input_dir data/coref_resolved_txts --ner_dir data/ner_coref_txts --output_dir results/named_people
```

This script will generate separate files for each textbook in the specified output directory, with counts of each named individual. It will also generate a file `full2wikiname.json` which saves aliases already queried from Wikidata allows you to rerun the script faster. 

If you would also like to obtain demographic information for the named individuals automatically, you can run the following script. This script builds on Wikidata, which has a lot of missing information (e.g. it usually doesn't specify race for white people), but it has high coverage of gender information, for example. The input should be the output of `count_names.py`. Names will be matched based on Wikidata aliases. 

```
python get_wikidata_attributes.py --input_dir results/named_people --output_dir results/ 
```

The output file will be a `.csv`, where the first column is the named entity as found in the text and the rest of the columns correspond to Wikidata attributes, including `gender`, `race/ethnicity`, and `occupation`. If the person was not found in the database, or the category was not listed, the value will be `None`. Note that the same person may show up multiple times if multiple Wikidata names are matched with it. 

# Looking at How People Are Described

## Verbs and Adjectives
One way to understand how people are described is to look at the verbs and adjectives that they co-occur with. For this, you first need to run dependency parsing. You can run the following script, where the format of the `people_terms` file should be the way it is described above. Our paper used Dozat et al. (2017)'s dependency parser. Since many of the other tools in this repo are based on SpaCy and it is time consuming to train a parser from scratch, the script we provide here uses SpaCy's dependency parser. 

```
python get_descriptors.py --input_dir data/ner_coref_txts --output_dir results/ --people_terms wordlists/people_terms.csv
```

This script will output `people_descriptors.csv` in the output directory, with the following columns:

* `source_text`: The name of the text file (corresponding to a textbook, for example). 
* `people_term`: The specific people term.
* `category`: The demographic category, or 'named' for named people. 
* `word`: The verb / adjective.
* `POS`: The part of speech tag for the word (ADJ or VERB).
* `relation`: The dependency parsing relation

Note that terms associated with multiple demographic categories would be listed multiple times. For example, "black woman" would be listed under both "black" and "women". The verbs include those that the person is performing (nsubj) and those that are performed on the person (dobj). 

The current implementation also obtains verbs and adjectives for named individuals, based on the output of the most popular named people of `count_names.py`. 

## Log odds ratio 

We can look at which words are significantly more associated with one group vs another group based on word counts (Monroe et al. 2009). The `--group1` and `--group2` arguments are two groups of labels (comma separated) that you want to compare. For example, the command below compares common nouns referring to women with all other categories we have for common nouns. If a descriptor falls under multiple labels (cases of intersectionality), it is included in the first group but not the second. For example, the script handles words referring to women that are marked by ethnicity by not including them in the second group. 

```
python run_log_odds.py --input_file results/people_descriptors.csv --output_dir results/ --group1 women --group2 "men,other,other minority,white,black,hispanic/latinx" 
```

The output file is `log_odds.txt` in the `results` folder.

Note that you need quotation marks if the input argument has a space in it. 

## Power, Agency and Sentiment 

Using external lexicons to quantify the affective connotations of words associated with people. 

We use two lexicons in our paper.

The first, the [NRC valence, arousal and dominance (VAD) lexicon](https://saifmohammad.com/WebPages/nrc-vad.html) contains a more than 20,000 English words. Download the zip file on their website and unzip it. Scores for words can be found in `NRC-VAD-Lexicon.txt` in the unzipped folder. 

The second, the [Connotation Frames dataset](https://homes.cs.washington.edu/~hrashkin/connframe.html) and [Power and Agency](https://homes.cs.washington.edu/~msap/movie-bias/) frames. Click on the `Full Labelled English Connotation Frame Data Set` link in the first link and the `download the verbs` link in the second. Once these downloads are unzipped, sentiment frames can be found in the file labeled `full_frame_info.txt` and agency and power frames are in the file `agency_power.csv`. 

Place these three lexicons (`full_frame_info.txt`, `NRC-VAD-Lexicon.txt`, and `agency_power.csv`) in the `wordlists` folder. 

```
python get_lexicon_averages.py --input_file results/people_descriptors.csv --output_dir results/
```

The script outputs a csv file in the output directory, called `lexicon_output.csv`, with the following columns:

* `demographic`: The demographic category. 
* `dimension`: Name of the dimension.
* `score`: Score for the particular dimension.
* `confidence_interval`: 95% confidence interval for the score.

Look at common verbs or adjectives associated with a category and their scores for some dimension: 

```
python get_lexicon_averages.py --input_file results/people_descriptors.csv --output_dir results/ --inspect True --category black --score_type agency
```

(Note that for power, the printed score is positive if the verb is power_agent, negative if power_theme, and the provided function does not take in account in which direction it is usually associated with the category of people.)

## Measure Association Between Words via Word Embeddings
Another way to measure association between words is to represent words as **vectors** and look at their distance in the vector space. For this, you first need to create vectors for the words in your text. You can do so by running the following script. Note that this will take a while, depending on your data size and number of runs you want to do.

```
python run_word2vec.py --input_dir data/final_txts --output_dir data/word2vec_models \
--num_runs 50 --dim 100 --bootstrap
```
The `input_dir` argument should be a directory that includes the txt files. The script will create separate model files for each training run in `output_dir`. 

By default, the script runs 50 separate bootstrap training runs -- this means that we sample from the sentences with replacement each time we train the model. This method, as found by [Antoniak and Mimno (2018)](https://mimno.infosci.cornell.edu/info3350/readings/antoniak.pdf), ensures that we can measure word associations robustly, and calculate significance values. You can decrease the number of runs. If you do not want to use bootstrapping, you can set the number of runs to 1 and remove the `--bootstrap` argument.

You can also change dimension size of the embeddings (by default, it's set to 100). If you decrease it, you *might* get slightly lower quality embeddings but they will take up less space. If you increase it, you *might* get embeddings that capture more subtle semantics, but they will take up more space.

To get the most closely associated word with a particular group, run the following script. Here, `words` is the comma-separated list of seed words that refer to that group or concept. The script will print out the top closest words and their mean cosine similarity across all model runs.

```
python word2vec_get_closest.py --words woman,women,she,her,hers --word2vec_dir data/word2vec_models
```

If you want to compare the similarity of words from various topics to two sets of terms (e.g. terms referring to men vs women), follow the following steps:

1. Create a dictionary file of terms referring to different themes, such as the one in `wordlists/liwc_queries.json`, in the following format. If you only have one category, that's fine too, but you still need to follow the same format. 

```
{
  "home": ["home", "domestic", "household", "chores", "family"],
  "work": ["work", "labor", "workers", "economy", "trade", "business",
           "jobs", "company", "industry", "pay", "working", "salary", "wage"],
  "achievement": ["power", "authority", "achievement", "control", "took control",
                  "won", "powerful", "success", "better", "efforts", "plan", "tried", "leader"],
}
```
2. Create two lists of words, one for one group of interest (e.g. women) and the other for the other group of interest (e.g. men). You can see examples in `wordlist/woman_terms.txt` and `wordlist/man_terms.txt`.

3. Run the following script, substituting the file references with your own paths. Change the arguments for `--name1` and `--name2` with your group names.

```
python word2vec_calculate_similarity.py --queries wordlists/liwc_queries.json \
--words1 wordlists/woman_terms.txt --words2 wordlists/man_terms.txt \
--name1 Women --name2 Men --word2vec_dir data/word2vec_models \
--output_file results/word2vec_cosines.csv
```

The script will save a dataframe in the file specified by `--output_file`, with the following columns:

* `<name1>`: Mean cosine similarity of query word to words in group 1.
* `<name2>`: Mean cosine similarity of query word to words in group 2.
* `query`: Query word.
* `word category`: Category that word belongs to.
* `p value`: *p* value for cosine similarity, calculated using two-tailed t test.


# Analyzing Topics

To induce topics in your data, you first need to run a topic model. Our script runs LDA, using the very efficient MALLET package. In order to run this, you first need to download MALLET. Download and unzip the most recent MALLET package [HERE](http://mallet.cs.umass.edu/download.php).

The following script runs the topic model:

```
python get_topics.py \
--mallet_dir /Users/<YOUR_USERNAME>/mallet-2.0.8/bin \
--num_topics 70 \
--input_dir data/coref_resolved_txts \
--output_dir topics/topics_70 \
--stem
```

where the arguments are the following:

* `mallet_dir`: Directory of the MALLET binary file.
* `num_topics`: Number of topics to induce.
* `input_dir`: Directory of textbook files.
* `output_dir`: Output directory for the topic model.
* `stem`: Whether to stem words before running the topic model (in the paper, we do).
 
The script will save the model and all associated files (e.g. vocabulary) in `output_dir`, and it will also create separate files for each book. You can inspect the topics in `output_dir/topic_names.json`, which contains the top 10 highest probability terms for each topic.

Note that this script runs the topic model on *all books* at once in `input_dir`, so if you want to get separate topic models for each book, then you should only include the relevant books in `input_dir`. If you want to run a topic model on all books, and then separate the topic distributions per book afterwards (this is what we did), you can do that with the script below.

## Topic Prominence

You can obtain the number of sentences where each topic is prominent (above a ratio of .1, as determined by the topic model) using the following script. 

```
python get_topic_prominence.py \
--topic_dir topics \
--textbook_dir data/coref_resolved_txts
```
where the arguments are the following:

* `topic_dir`: Directory containing the topic files.
* `textbook_dir`: Directory containing the textbook files (for the purposes of obtaining titles).

The script will generate a dataframe, with the following columns:

* `book`: Title of the book.
* `topic_id`: ID of the topic, as in `topics/topic_names.json`.
* `topic_words`: Top words associated with the topic, as in `topics/topic_names.json`.
* `raw_count`: Raw number of sentences where the topic is prominent for the given book.
* `topic_proportion`: The proportion of sentences where the topic is prominent for the given book.








