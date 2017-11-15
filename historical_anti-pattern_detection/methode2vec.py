from pyspark.mllib.feature import Word2Vec
from pyspark import SparkContext

#import collections
import reader

sc = SparkContext()
rdd = sc.textFile("./data.txt").map(lambda row: row.split(" "))
#data = reader.getData('./systems_history/frameworks-base.csv')
#rdd = sc.parallelize(List(data)).collect()


word2vec = Word2Vec()
word2vec.setMinCount(25)
word2vec.setLearningRate(0.025)
word2vec.setVectorSize(8)
model = word2vec.fit(rdd)