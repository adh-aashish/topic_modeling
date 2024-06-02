import pandas as pd
import pickle
from gensim import models 

def load_data(relative_path='../results/'):
    processed_data = pd.read_pickle(relative_path+"processed_data.pkl")
    bow_path = relative_path+"bow_corpus.pkl"
    id2word_path = relative_path+"id2word.pkl"

    with open(bow_path, 'rb') as f:
        bow_corpus= pickle.load(f)

    with open(id2word_path, 'rb') as f:
        id2word = pickle.load(f)

    return processed_data, bow_corpus, id2word



# model topic num is put 26 for now as default to not break wherever it is called for now
# WIP: put no default and make it a required parameter.
def load_lda_bow(relative_path="../results/"):
    
    model_topic_num=None
    with open(f'{relative_path}current_model_topic_num.txt', 'r', encoding='utf-8') as file:
        number_str = file.read().strip()
        model_topic_num = int(number_str)
    
    model_file_name = relative_path+"models/bow_" + str(model_topic_num)
    lda_model = models.ldamodel.LdaModel.load(model_file_name)
    return lda_model