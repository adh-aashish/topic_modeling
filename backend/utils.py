import re
import csv
import ast
import gensim
from gensim import models,corpora
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

# global variables section
if __name__=="utils":
    nepali_stopwords = open("../resources/stopwords.txt", "r")
    stopwords = nepali_stopwords.read().split()
    lda_model = models.ldamodel.LdaModel.load('../saved_model/lda_model_politics_1')
    id2word = corpora.Dictionary.load('../saved_model/dictionary_1')
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
        img_paths = [folder_path+'/'+i for i in os.listdir(folder_path)]
    # print(img_paths)
    encoded_imgs = []
    for image_path in img_paths:
        # encoded_imgs.append(get_response_image(image_path))
        with open(image_path,'rb') as imgfile:
            data = base64.b64encode(imgfile.read()).decode('utf-8')
            encoded_imgs.append(data)
    
    return encoded_imgs


def get_topics_bar_chart_by_percentage(topic_distribution):
    fig, ax = plt.subplots()
    topics = ['Topic-'+str(idx) for idx, score in topic_distribution]
    score = [score * 100 for idx, score in topic_distribution]
    num_bars = len(topic_distribution)
    random_colors = [np.random.rand(3,) for _ in range(num_bars)]

    ax.bar(topics, score, color=random_colors)

    ax.set_ylabel('Topic percentage in Document')
    ax.set_title('Constituent percentage of topics in a Document')
    ax.legend(title='Percentage')

    plt.savefig('./generated_info/topic_dis_percentage.png',
                bbox_inches='tight')
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
    list_of_images = []
    for i in top_topics_in_a_doc:
        topic_in_dict_form = dict(lda_model.show_topic(i[0], 20))
        plt.axis('off')
        plt.imshow(
            WordCloud(font_path="../resources/Mangal.ttf").fit_words(topic_in_dict_form))
        random_img_name = shortuuid.uuid()+'.png'
        random_img_path = f'./generated_info/word_clouds/{random_img_name}'
        plt.savefig(random_img_path, bbox_inches='tight')
    list_of_images = images_to_base64_list(
        folder_path='./generated_info/word_clouds/')
    return list_of_images
