import load_variables

processed_data, bow_corpus, id2word, lda_model = load_variables.load_data()

cooccurrence_count = {}
for corpus in bow_corpus:
    topic_distribution = lda_model.get_document_topics(corpus, minimum_probability=0.45)
    for i in range(len(topic_distribution)-1):
        for j in range(i+1 , len(topic_distribution)):
            tup = (topic_distribution[i][0], topic_distribution[j][0])
            if tup not in cooccurrence_count:
                cooccurrence_count[tup] = 0 
            cooccurrence_count[tup] = cooccurrence_count[tup] + 1

cooccurrence_count = dict(sorted(cooccurrence_count.items(), key=lambda item: item[1], reverse=True))

print(cooccurrence_count)
