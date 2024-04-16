import pandas as pd
from gensim import corpora, models
import pickle
import matplotlib.pyplot as plt
from utils.load_variables import load_lda_bow

processed_data = pd.read_pickle("../results/processed_data.pkl")
processed_data_list = processed_data["body"]

df = pd.read_csv("../data/news-setopati/news_setopati_preprocessed_1.csv")

cluster_by_topic = {}
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

'''
bag-of-words format = list of (token_id, token_count) 2-tuples
'''
bow_corpus = [id2word.doc2bow(sent) for sent in processed_data_list]

'''
Loading the model
'''
# model_file_name = "../results/models/bow_26"
# lda_model = models.ldamodel.LdaModel.load(model_file_name)
lda_model = load_lda_bow()

###################################################
# cluster each news accoroding to year and topic_id 
###################################################

cluster_file_path = '../results/analysis/cluster_by_year.pkl'
# cluster_by_year = {
#     2080 : [(i, []) for i in range(lda_model.num_topics)],
#     2079 : [(i, []) for i in range(lda_model.num_topics)],
#     2078 : [(i, []) for i in range(lda_model.num_topics)],
#     2077 : [(i, []) for i in range(lda_model.num_topics)],
#     2076 : [(i, []) for i in range(lda_model.num_topics)],
#     2075 : [(i, []) for i in range(lda_model.num_topics)]
# }

# [cluster_by_topic.setdefault(i, []) for i in range(lda_model.num_topics)]

# def get_nepali_year(index):
#     global df;
#     date = df.loc[index, "date"]
#     return date[-4:]

# def devnagari_to_english(date):
#     nepali_to_english = {
#         '०': '0',
#         '१': '1',
#         '२': '2',
#         '३': '3',
#         '४': '4',
#         '५': '5',
#         '६': '6',
#         '७': '7',
#         '८': '8',
#         '९': '9'
#     }
#     eng_date = ""
#     for i in range(len(date)):
#         eng_date = eng_date + nepali_to_english[date[i]]
#     return int(eng_date)
# index = 0
# for bow in bow_corpus:
#     unprocessed_nepali_year = get_nepali_year(index);
#     date = devnagari_to_english(unprocessed_nepali_year)
#     topics_list = lda_model.get_document_topics(bow,minimum_probability=0.7)
#     for topic_id, score in topics_list: 
#         cluster_by_year[date][topic_id][1].append(df.loc[index,"title"])
#     index += 1

# print(cluster_by_year)

# File path to save the pickle file

# Open the file in binary write mode and save the dictionary using pickle.dump()
# with open(cluster_file_path, 'wb') as f:
#     pickle.dump(cluster_by_year, f)

with open(cluster_file_path, 'rb') as f:
    cluster_by_year = pickle.load(f)

document_count_by_year_path = "../results/analysis/document_count_by_year.pkl"

# count the frequency of document per year, per topic

# document_count_by_year = {}
# for k,v in cluster_by_year.items():
#     document_count_by_year[k] = [(i,len(v[i][1])) for i in range(len(v))]

# print(document_count_by_year)

# with open(document_count_by_year_path, 'wb') as f:
#     pickle.dump(document_count_by_year, f)

with open(document_count_by_year_path, 'rb') as f:
    document_count_by_year = pickle.load(f)

# print(document_count_by_year)

years = sorted(document_count_by_year.keys())
topics_num = 26
topics_idx = range(topics_num)

######################################
# Trend of each topics over the years
######################################

for year in years:
    year_data = document_count_by_year[year]
    topic_count = [count[1] for count in year_data]
    plt.plot(topics_idx, topic_count, label=str(year))

# plt.xlabel('Topic idx')
# plt.ylabel('Document Frequency')
# plt.title('Trend of each topics over the years')
# plt.legend(title='Year')
# plt.grid(True)
# plt.savefig("../results/visualization/document_count_per_year.png")

####################################
# Per Topic Trend over the years 
####################################

per_topic_document_count = {}
for topic_id in topics_idx:
    topic_count = [document_count_by_year[year][topic_id][1] for year in years]
    plt.xlabel('Year')
    plt.ylabel('Frequency of Documents')
    plt.plot(years, topic_count)
    plt.title(f'Trend of Topic id : {topic_id + 1}')
    plt.grid(True)
    plt.savefig(f"../results/visualization/per_topic_trend/{topic_id}.png")
    plt.clf()