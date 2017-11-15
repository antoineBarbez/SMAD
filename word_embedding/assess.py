from sklearn.manifold import TSNE
from model import Java2Vec
import matplotlib.pyplot as plt


def plot_with_labels(low_dim_embs, labels, filename='tsne.png'):
  assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
  plt.figure(figsize=(18, 18))  # in inches
  for i, label in enumerate(labels):
    x, y = low_dim_embs[i, :]
    plt.scatter(x, y)
    plt.annotate(label,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

  plt.savefig(filename)

def visualize_embedding(pickle_file='embedding_model.pickle', nb_word=50):

  model = Java2Vec(pickle_file)

  tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000, method='exact')
  plot_only = nb_word
  low_dim_embs = tsne.fit_transform(model.vector_space[:plot_only, :])
  labels = [model.line_to_word[i] for i in xrange(plot_only)]
  plot_with_labels(low_dim_embs, labels)



if __name__ == "__main__":
  visualize_embedding('embedding_model.pickle', nb_word=84)