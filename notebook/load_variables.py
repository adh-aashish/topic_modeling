import pandas as pd
import pickle
from gensim import models 

def load_data():
    processed_data = pd.read_pickle("./results/processed_data.pkl")
    bow_path = "./results/bow_corpus.pkl"
    id2word_path = "./results/id2word.pkl"

    with open(bow_path, 'rb') as f:
        bow_corpus= pickle.load(f)

    with open(id2word_path, 'rb') as f:
        id2word = pickle.load(f)

    
    model_file_name = "./results/models/bow_26"
    lda_model = models.ldamodel.LdaModel.load(model_file_name)

    return processed_data, bow_corpus, id2word, lda_model