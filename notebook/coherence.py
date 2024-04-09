import matplotlib.pyplot as plt

topic_count = [i for i in range(20, 40, 2)]
coherence_score = [0.56382, 0.59101, 0.59208, 0.60092, 0.58553, 0.57459, 0.56106, 0.57778, 0.587133, 0.575706]
print(topic_count, coherence_score)
plt.xlabel('Number of Topics')
plt.ylabel('Coherence Score')
plt.plot(topic_count, coherence_score)
plt.title(f'Number of topics vs Coherence Score')
plt.grid(True)
plt.xticks(range(min(topic_count), max(topic_count)+1, 1))
plt.savefig(f"./results/visualization/coherence_score.png")
plt.clf()