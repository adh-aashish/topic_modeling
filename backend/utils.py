import re
import csv
import ast
import gensim
from gensim import models
import pandas as pd
import snowballstemmer
from nepalitokenizer import NepaliTokenizer
import glob
import os
import base64

# global variables section
if __name__=="utils":
    nepali_stopwords = open("../resources/stopwords.txt", "r")
    stopwords = nepali_stopwords.read().split()
    lda_model = models.ldamodel.LdaModel.load('../saved_model/lda_model_politics_1')
    df = pd.read_csv("../data/news-setopati/news-setopati-processed.csv")
    stemmer = snowballstemmer.NepaliStemmer()
    tokenize = NepaliTokenizer()

# important functions

def get_stem(words,stemmer):
    new_list = stemmer.stemWords(words)
    return new_list

def clean_data(words,stopwords):
    new_list = []
    for word in words:
        if len(word) > 2 and word not in stopwords:
            new_list.append(word)

    return new_list


def string_manipulation(unprocessed_data):
    unprocessed_data['body'] = unprocessed_data['body'].apply(
        lambda x: re.sub('[।(),०-९<<?!,—,–,/,’,‘,:,\u200d]', '', x))
    unprocessed_data['body'] = unprocessed_data['body'].apply(lambda x: " ".join([i.replace(
        '\n', '').replace('\t', '').replace("\"", '') for i in x.split() if i not in (stopwords) and i != ' ']))
    return unprocessed_data


def read_bow_corpus():
    bow_corpus = []
    with open('../saved_model/bow_corpus_1.txt', 'r') as file:
        for line in file:
            bow_corpus.append(ast.literal_eval(line.strip()))
    return bow_corpus

def store_top_five_news(lda_model) -> bool:
    try:
        bow_corpus = read_bow_corpus()
        my_ids = [i for i in range(len(bow_corpus))]
        top_documents = {}
        [top_documents.setdefault(i, []) for i in range(lda_model.num_topics)]

        for topic_id in range(lda_model.num_topics):
            tops = sorted(zip(my_ids, lda_model[bow_corpus]), reverse=True, key=lambda x: abs(
                dict(x[1]).get(topic_id, 0.0)))
            top_five = tops[: 5]
            for index, _ in top_five:
                top_documents[topic_id].append(index)

        with open('../saved_model/top_five_doc.txt','w',encoding='UTF8') as file:
            writer = csv.writer(file)
            header =["topic_id","news1","news2","news3","news4","news5"]
            # write the header
            writer.writerow(header)
            for k,v in top_documents.items():
                top_news = [k]
                for index in v:
                    top_news.append(df['title'][index])
                writer.writerow(top_news)
    except Exception as e:
        print('Exception caught, it is: ',e)
        return False
    print('Success in storing top 5 news headlines')
    return True



def clear_folder(folder_path:str='./generated_info'):
    # print(folder_path+'*')
    files = glob.glob(folder_path+'/*')
    for f in files:
        os.remove(f)
    return {"success":True,"files":files}

def images_to_base64_list(folder_path:str='./generated_info/'):
    # print('!!!!!!!!!!!!!!!!!!!!!!')
    # print(os.listdir(folder_path))
    # print(folder_path)
    # print('!!!!!!!!!!!!!!!!!!!!!!')
    # this way works for base64 encoded image
    img_paths = [folder_path+'/'+i for i in os.listdir(folder_path)]
    # print(img_paths)
    encoded_imgs = []
    for image_path in img_paths:
        # encoded_imgs.append(get_response_image(image_path))
        with open(image_path,'rb') as imgfile:
            data = base64.b64encode(imgfile.read()).decode('utf-8')
            encoded_imgs.append(data)
    
    return encoded_imgs
