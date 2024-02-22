import os
import pandas as pd
from gensim import corpora, models
import gensim
from gensim.models import CoherenceModel
import pickle

processed_data = pd.read_pickle("./results/processed_data.pkl")
processed_data_list = processed_data["body"]

'''
Representing the Corpus in dictionary: 
{unique_id : word}
'''
id2word = corpora.Dictionary(processed_data_list)

'''
Remove very rare and very common words:

- words appearing less than 15 times
- words appearing in more than 10% of all documents
'''
id2word.filter_extremes(no_below=15, no_above=0.1, keep_n=None)

with open("./results/id2word.pkl", 'wb') as f:
    pickle.dump(id2word, f)

'''
bag-of-words format = list of (token_id, token_count) 2-tuples
'''
bow_corpus = [id2word.doc2bow(sent) for sent in processed_data_list]

with open("./results/bow_corpus.pkl", 'wb') as f:
    pickle.dump(bow_corpus, f)

# topic_num = 22
# for topic_num in range(24,40,2):
#     model_file_name = "./results/models/bow_"+str(topic_num)

#     '''
#     Loading the model
#     '''
#     # lda_model = models.ldamodel.LdaModel.load(model_file_name)

#     '''
#     Training the model
#     '''
#     lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=topic_num, id2word=id2word, passes=20)
#     #saving the model
#     lda_model.save(model_file_name)

#     '''
#     Saving the topics 
#     '''
#     topic_file_name = "./results/topics/bow_" + str(topic_num) + ".txt"
#     mode = 'a' if os.path.exists(topic_file_name) else 'w'
#     with open(topic_file_name, mode) as topic_file:
#         for idx, topic in lda_model.print_topics(-1):
#             topic_file.write("Topic id : {} ".format(idx))
#             topic_file.write("Words: {} \n".format(topic))
#             topic_file.write("\n")

#     texts = processed_data.body.values.tolist()

#     coherence_model_lda = CoherenceModel(model=lda_model, corpus=bow_corpus, texts=texts, dictionary=id2word, coherence='c_v')
#     #saving coherence score
#     coherence_file_name = "./results/coherence/coherence.txt"
#     mode = 'a' if os.path.exists(coherence_file_name) else 'w'
#     with open(coherence_file_name, mode) as coherence_file:
#         coherence_file.write(f"BOW, {topic_num} topics : {coherence_model_lda.get_coherence()}\n")