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
import base64
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import shortuuid
import logging
from scipy.stats import entropy
from scipy.spatial import distance

# global variables section
if __name__=="utils":
    logging.basicConfig(level=logging.CRITICAL, filename='./file.log',filemode='w', format='%(levelname)s - %(message)s')
    nepali_stopwords = open("../resources/stopwords.txt", "r")
    stopwords = nepali_stopwords.read().split()
    lda_model = models.ldamodel.LdaModel.load('../saved_model/lda_model_politics_2')
    id2word = corpora.Dictionary.load('../saved_model/dictionary_2')
    df = pd.read_csv("../data/news-setopati/news_setopati_preprocessed_1.csv")
    stemmer = snowballstemmer.NepaliStemmer()
    tokenize = NepaliTokenizer()
    
    # reading bow_corpus
    file_path = '../saved_model/bow_corpus_2.txt'
    with open(file_path, 'r') as file:
        lines = file.readlines()
    bow_corpus = pd.Series(lines, name='body')

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
    x = ast.literal_eval(x.strip())
    return x

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



def clear_folder(folder_path:str='./generated_info/word_clouds'):
    # print(folder_path+'*')
    files = glob.glob(folder_path+'/*')
    for f in files:
        os.remove(f)
    return {"success":True,"files":files}

def images_to_base64_list(file_path:str|None = None, folder_path:str | None=None):
    # print('!!!!!!!!!!!!!!!!!!!!!!')
    # print(os.listdir(folder_path))
    # print(folder_path)
    # print('!!!!!!!!!!!!!!!!!!!!!!')
    # this way works for base64 encoded image
    if file_path:
        img_paths = [file_path]
    else:
        img_paths = [folder_path+i for i in os.listdir(folder_path)]
    # print('-----------')
    # print(img_paths)
    # print('-----------')
    encoded_imgs = [] # [(score, encoded_image)]
    # encoded_imgs_path = []
    for image_path in img_paths:
        # encoded_imgs.append(get_response_image(image_path))
        # if folder_path:
        #     score = map_image_path_score[image_path]
        # else:
        #     score = ''
        with open(image_path,'rb') as imgfile:
            data = base64.b64encode(imgfile.read()).decode('utf-8')
            if folder_path:
                encoded_imgs.append([image_path, data])
                # encoded_imgs_path.append(image_path)
            else:
                encoded_imgs.append(data)
    # if folder_path:
    #     return encoded_imgs_path,encoded_imgs
    return encoded_imgs


def get_topics_bar_chart_by_percentage(topic_distribution):
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
    for i in top_topics_in_a_doc:
        topic_in_dict_form = dict(lda_model.show_topic(i[0], 20))
        plt.axis('off')
        plt.imshow(
            WordCloud(font_path="../resources/Mangal.ttf").fit_words(topic_in_dict_form))
        random_img_name = shortuuid.uuid()+'.png'
        random_img_path = f'./generated_info/word_clouds/{random_img_name}'
        plt.savefig(random_img_path, bbox_inches='tight')
        map_image_path_score[random_img_path] = i[1]
    
        img_info = images_to_base64_list(
        folder_path='./generated_info/word_clouds/')
    
    for i in range(len(img_info)):
        img_info[i][0] = float(map_image_path_score[img_info[i][0]])
        
    # now sort to make first image to have highest score
    # l = [[0.4, 'a'], [0.5, 'c'], [0.87, 'c']]
    sorted_img_info = sorted(img_info, key=lambda x: x[0], reverse=True)

    # print(sorted_img_info)

    score_values = [i for i,j in sorted_img_info]
    logging.critical(score_values)
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
    df_doc_topic = pd.read_csv('../saved_model/doc_topic_distribution_39k.csv')
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
        info = [df['title'][ids],df['date'][ids],df['link'][ids],df['source'][ids]]
        required_info.append(info)
    
    
    return required_info

# get similar news section--------------------