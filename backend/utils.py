import re
import csv
import ast
import gensim
from gensim import models,corpora
from fastapi.responses import JSONResponse
import pandas as pd
import snowballstemmer
from nepalitokenizer import NepaliTokenizer
import glob
import os
from os import path
import base64
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import shortuuid
import logging
from scipy.stats import entropy
from scipy.spatial import distance

import sys
# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from notebooks.load_variables import load_data

# global variables section
if __name__=="utils":
    logging.basicConfig(level=logging.CRITICAL, filename='./file.log',filemode='w', format='%(levelname)s - %(message)s')
    nepali_stopwords = open("../resources/stopwords.txt", "r")
    stopwords = nepali_stopwords.read().split()
    # lda_model = models.ldamodel.LdaModel.load('../saved_model/lda_model_politics_2')
    processed_data, bow_corpus, id2word, lda_model = load_data(relative_path='../notebooks/results/')
    # id2word = corpora.Dictionary.load('../saved_model/dictionary_2')
    # df = pd.read_csv("../data/news-setopati/news_setopati_preprocessed_1.csv")
    df = pd.read_csv("../data/news-setopati/news_setopati_40k_year_month.csv")
    stemmer = snowballstemmer.NepaliStemmer()
    tokenize = NepaliTokenizer()
    NUM_TOP_DOCS = 8
    
    # reading bow_corpus [ PAST way before modularizing by load_variables.py ]
    # file_path = '../saved_model/bow_corpus_2.txt'
    # with open(file_path, 'r') as file:
    #     lines = file.readlines()
    # bow_corpus = pd.Series(lines, name='body')

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


def return_bow(index):
    # bow_corpus = []
    # with open('../saved_model/bow_corpus_2.txt', 'r') as file:
    #     for line in file:
    #         bow_corpus.append(ast.literal_eval(line.strip()))
    # return bow_corpus
    x = bow_corpus[index]
    # x = ast.literal_eval(x.strip())
    # print(x)
    return x


def store_top_news_per_topic():
    # VVI : TODO: need to put year, month column in df [ Did this in test-top-news-per-topic.ipynb manually but need to include that functionality here too. ]
    try:
        # NUM_TOP_DOCS variable is set above as constant
        cluster_by_topic = {}
        [cluster_by_topic.setdefault(i, []) for i in range(lda_model.num_topics)]
        index = 0
        num_of_docs = df.shape[0]
        
        print('Fine till here')
        for i in range(num_of_docs):
            print(f'Fine till here = {i}')
            bow = return_bow(i)
            
            topics_list = lda_model.get_document_topics(bow, minimum_probability=0.8)
            for topic_id, score in topics_list:
                cluster_by_topic[topic_id].append((index,score))
            index += 1
        # print('Fine till here')
        top_docs = []
        for i in cluster_by_topic:
            curr_top_docs = cluster_by_topic[i]
            # Sort the list by the second element of each tuple in descending order
            curr_top_docs = sorted(curr_top_docs, key=lambda tup: tup[1], reverse=True)[0:NUM_TOP_DOCS]
            cluster_by_topic[i] = curr_top_docs
            for index,score in curr_top_docs:
                top_docs.append([i,score,df['title'][index], df['date'][index],df['link'][index], df['source'][index]])
            
        result_df = pd.DataFrame(top_docs, columns=[
                        'topic_no', 'score', 'title', 'date', 'link', 'source'])
        result_df.to_csv(
            './generated_info/top_news_per_topic_26_topics_setopati_1.csv', index=False)
    except Exception as e:
        if path.exists('./generated_info/top_news_per_topic_26_topics_setopati_1.csv'):
            os.remove(
                './generated_info/top_news_per_topic_26_topics_setopati_1.csv')
        return False
    return True


def clear_folder(folder_path:str='./generated_info/word_clouds'):
    # print(folder_path+'*')
    try:
        files = glob.glob(folder_path+'/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        return False
    return True

def get_topic_trend_image(id):
    return images_to_base64_list(f'../notebooks/results/visualization/per_topic_trend/{id}.png')[0]
    
def images_to_base64_list(file_path:str|None = None, folder_path:str | None=None):
    if file_path:
        img_paths = [file_path]
    else:
        img_paths = [folder_path+i for i in os.listdir(folder_path)]
        print('-------######-------')
        img_idxs = [int((re.search(r'\d+', i.split('/')[-1].split('-')[-1])).group()) for i in img_paths]
        print('Inside func: images_to_base64_list: ', img_idxs)
        print('-------######-------')

    encoded_imgs = [] # [(score, encoded_image)]
    for i in range(len(img_paths)):

        with open(img_paths[i],'rb') as imgfile:
            data = base64.b64encode(imgfile.read()).decode('utf-8')
            if folder_path:
                encoded_imgs.append([img_paths[i], data, img_idxs[i]-1])
                # encoded_imgs_path.append(image_path)
            else:
                encoded_imgs.append(data)
    # print(encoded_imgs)
    # print(encoded_imgs)
    return encoded_imgs


def get_topics_bar_chart_by_percentage(topic_distribution):
    """
    Given top_topic_distribution of a news document, return a barchart image of top topics ,where score
    is greater than 0.05
    """
    fig, ax = plt.subplots()
    topics = ['Topic-'+str(idx) for idx, score in topic_distribution if score > 0.05]
    score = [score * 100 for idx, score in topic_distribution if score > 0.05 ]
    num_bars = len(topic_distribution)
    random_colors = [np.random.rand(3,) for _ in range(num_bars)]

    ax.bar(topics, score, color=random_colors)

    ax.set_ylabel('Topic percentage in Document')
    ax.set_title('Constituent percentage of topics in a Document')
    ax.legend(title='Percentage')

    plt.savefig('./generated_info/topic_dis_percentage.png',
                bbox_inches='tight')
    ax.cla()
    image = images_to_base64_list(
        file_path='./generated_info/topic_dis_percentage.png')[0]
    return image



def get_processed_data(df):
    df['body'] = df['body'].apply(str)
    processed_data = string_manipulation(df)
    processed_data = processed_data['body'].to_list()[0]
    processed_data = tokenize.tokenizer(processed_data)
    processed_data = get_stem(processed_data, stemmer)
    processed_data = clean_data(processed_data, stopwords)
    return processed_data


def get_imgs_of_topics_word_cloud(top_topics_in_a_doc):
    map_image_path_score ={}
    idx_list = []
    for i in top_topics_in_a_doc:
        topic_in_dict_form = dict(lda_model.show_topic(i[0], 20))
        idx_list.append(i[0])
        plt.axis('off')
        plt.imshow(
            WordCloud(font_path="../resources/Mangal.ttf").fit_words(topic_in_dict_form))
        random_img_name = shortuuid.uuid()+'.png'
        random_img_path = f'./generated_info/word_clouds/{random_img_name}'
        plt.savefig(random_img_path, bbox_inches='tight')
        map_image_path_score[random_img_path] = [i[0],i[1]]
    
    img_info = images_to_base64_list(
        folder_path='./generated_info/word_clouds/')
    
    count = 0
    for i in range(len(img_info)):
        img_info[i][2] = int(map_image_path_score[img_info[i][0]][0])
        img_info[i][0] = float(map_image_path_score[img_info[i][0]][1])
        # img_info[i].append(idx_list[count])
        count+=1
        
    # now sort to make first image to have highest score
    # l = [[0.4, 'a'], [0.5, 'c'], [0.87, 'c']]
    sorted_img_info = sorted(img_info, key=lambda x: x[0], reverse=True)

    # print(sorted_img_info)

    # score_values = [i for i,j in sorted_img_info]
    # logging.critical(score_values)
    return sorted_img_info


# get similar news section--------------------
def jensen_shannon(query, matrix):
    """
    This function implements a Jensen-Shannon similarity
    between the input query (an LDA topic distribution for a document)
    and the entire corpus of topic distributions.
    """
    sim = [distance.jensenshannon(data,query) for data in matrix]
    return np.array(sim)

def get_most_similar_documents(query,matrix,k=10):
    """
    This function implements the Jensen-Shannon distance above
    and retruns the top k indices of the smallest jensen shannon distances
    """
    sims = jensen_shannon(query,matrix) # list of jensen shannon distances
    return sims.argsort()[:k] # the top k positional index of the smallest Jensen Shannon distances



def get_similar_news(bow_vector):
    '''
    Give bow_vector of a news, then get its similar other news from trained dataset of ~40k news from setopati
    '''
    # used jensen shannon distance to calculate similar documents
    df_doc_topic = pd.read_csv('../saved_model/doc_topic_distribution_39k_26topics.csv')
    doc_distribution = df_doc_topic.values.tolist()
    # bow_vector = id2word.doc2bow(processed_news)
    new_dist = []
    for idx,score in lda_model.get_document_topics(bow_vector,minimum_probability=0):
        new_dist.append(score)

    new_doc_distribution = np.array(new_dist)
    
    most_sim_ids = get_most_similar_documents(new_doc_distribution,doc_distribution)


    required_info = []
    # print(most_sim_ids)
    for ids in most_sim_ids:
        info = {'title': df['title'][ids],'date':df['date'][ids],'link':df['link'][ids],'source':df['source'][ids]}
        required_info.append(info)
    
    
    return required_info

# get similar news section--------------------
