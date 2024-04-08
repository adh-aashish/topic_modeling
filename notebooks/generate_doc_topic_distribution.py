from load_variables import load_data
processed_data, bow_corpus, id2word, lda_model = load_data()


import numpy as np
import pandas as pd

'''
Obtaining the topic distribution of every document
'''
doc_topic_dist = []
count = 0
for bow in bow_corpus:
    topics_list = lda_model.get_document_topics(bow, minimum_probability=0)
    # print(topics_list)
    # print(len(topics_list))
    # if count > 2:
    #     break
    # count += 1
    row = []
    for idx, score in topics_list:
        row.append(score)

    doc_topic_dist.append(row)

print(len(doc_topic_dist))

doc_distribution = np.array(doc_topic_dist)

df_temp = pd.DataFrame(doc_distribution)
df_temp.to_csv('../saved_model/doc_topic_distribution_39k_26topics.csv',index=False,index_label=None)
