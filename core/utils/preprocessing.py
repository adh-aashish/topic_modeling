import pandas as pd
import nltk
import re
from nepalitokenizer import NepaliTokenizer
import snowballstemmer

#loading the data
df = pd.read_csv("../data/news-setopati/news_setopati_preprocessed_1.csv")
unprocessed_data = pd.DataFrame(columns=['body'])
unprocessed_data["body"] = df["body"].apply(str)

#preprocessing
nepali_stopwords = open("../resources/stopwords.txt", "r")
stopwords = nepali_stopwords.read().split()

def get_stem(words):
    '''
    Performs stemming
    '''
    stemmer = snowballstemmer.NepaliStemmer()
    new_list = stemmer.stemWords(words)
    return new_list


def clean_data(words):
    '''
    Removes stop words
    '''
    new_list = []
    for word in words:
        if len(word)>2 and word not in stopwords:
            new_list.append(word)
    return new_list

def string_manipulation(unprocessed_data): 
    tokenize = NepaliTokenizer()
    unprocessed_data['body'] = unprocessed_data['body'].apply(lambda x: re.sub('[।(),०-९<<?!,—,–,/,’,‘,:,\u200d]', '', x))
    unprocessed_data['body'] = unprocessed_data['body'].apply(lambda x: " ".join([i.replace('\n', '').replace('\t', '').replace("\"",'') for i in x.split() if i not in (stopwords) and i != ' ']))
    unprocessed_data["body"] = unprocessed_data["body"].apply(tokenize.tokenizer)
    unprocessed_data['body'] = unprocessed_data['body'].apply(lambda x : get_stem(x))
    unprocessed_data['body'] = unprocessed_data['body'].apply(lambda x : clean_data(x))
    return unprocessed_data

processed_data = string_manipulation(unprocessed_data)
processed_data.to_pickle("./results/processed_data.pkl")