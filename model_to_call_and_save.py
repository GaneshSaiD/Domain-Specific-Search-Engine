import gensim
from gensim import models
from gensim import corpora
from gensim.models.doc2vec import Doc2Vec
from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import Doc2Vec
from gensim.corpora import Dictionary
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix
from gensim.similarities import WmdSimilarity
import gensim.downloader as api
from gensim.models import KeyedVectors
import gensim.downloader as api
from gensim.models.doc2vec import Doc2Vec



w2v_model_300 = api.load("glove-wiki-gigaword-300")
model300=w2v_model_300
model300.save_word2vec_format('model300.bin', binary=True)
print("model 300 tained")
