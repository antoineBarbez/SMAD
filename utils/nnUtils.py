from context               import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import numpy             as np
import tensorflow        as tf
import matplotlib.pyplot as plt

import dataUtils
import random
import sys

### EVALUATION ####
def true_positive(output, labels):
	tp = tf.cast(tf.equal(tf.argmax(output,1) + tf.argmax(labels,1), 0), tf.float32)

	return tp

def precision(output, labels):
	tp = true_positive(output, labels)
	detected = tf.cast(tf.equal(tf.argmax(output,1), 0), tf.float32)

	return tf.reduce_sum(tp)/tf.reduce_sum(detected)

def recall(output, labels):
	tp = true_positive(output, labels)
	positive = tf.cast(tf.equal(tf.argmax(labels,1), 0), tf.float32)

	return tf.reduce_sum(tp)/tf.reduce_sum(positive)

def f_measure(output, labels):
	prec = precision(output, labels)
	rec = recall(output, labels)

	return 2*prec*rec/(prec+rec)

def accuracy(output, labels):
	correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(labels,1))

	return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))


### UTILS ###
def shuffle(X, Y):
	assert len(X) == len(Y), 'X and Y must have the same number of elements'

	idx = range(len(X))
	random.shuffle(idx)

	shuffled_X = np.array([X[i] for i in idx])
	shuffled_Y = np.array([Y[i] for i in idx])
	
	return shuffled_X, shuffled_Y

# Returns the Bayesian averaging between many network's predictions
def ensemble_prediction(model, save_paths, input_x):
	saver = tf.train.Saver(max_to_keep=len(save_paths))
	predictions = []
	with tf.Session() as session:
		for save_path in save_paths:
			saver.restore(sess=session, save_path=save_path)
			prediction = session.run(model.inference, feed_dict={model.input_x: input_x})
			predictions.append(prediction)

	return np.mean(np.array(predictions), axis=0)

def plot_learning_curves(losses_train, losses_test):
	plt.figure()
	plt.ylim((0.0, 1.0))
	plt.xlabel("Epochs")
	plt.ylabel("Loss")
	mean_train = np.mean(losses_train, axis=0)
	mean_test = np.mean(losses_test, axis=0)
	percentile90_train = np.percentile(losses_train, 90, axis=0)
	percentile90_test  = np.percentile(losses_test, 90, axis=0)
	percentile10_train = np.percentile(losses_train, 10, axis=0)
	percentile10_test = np.percentile(losses_test, 10, axis=0)
	plt.grid()

	plt.fill_between(range(len(losses_train[0])), percentile90_train,
	                 percentile10_train, alpha=0.2,
	                 color="r")
	plt.fill_between(range(len(losses_test[0])), percentile90_test,
	                 percentile10_test, alpha=0.2,
	                 color="g")
	plt.plot(range(len(losses_train[0])), mean_train, color="r", label='Training set')
	plt.plot(range(len(losses_test[0])), mean_test, color="g", label='Test set')
	plt.legend(loc='best')
	plt.show()


### INSTANCES AND LABELS GETTERS ###

# Get labels in vector form for a given system
# antipattern in ['god_class', 'feature_envy']
def getLabels(systemName, antipattern):
	assert antipattern in ['god_class', 'feature_envy']

	if antipattern == 'god_class':
		entities = dataUtils.getClasses(systemName)
	else:
		entities = dataUtils.getCandidateFeatureEnvy(systemName)

	labels = []
	true = dataUtils.getAntipatterns(systemName, antipattern)
	for entity in entities:
		if entity in true:
			labels.append([1, 0])
		else:
			labels.append([0, 1])

	return np.array(labels)


def getInstances(systemName, antipattern, normalized=True):
	assert antipattern in ['god_class', 'feature_envy']

	metrics = []
	if antipattern == 'god_class':
		entities = dataUtils.getClasses(systemName)
		metrics.append(dataUtils.getGCDecorMetrics(systemName))
		metrics.append(dataUtils.getGCHistMetrics(systemName))
		metrics.append(dataUtils.getGCJDeodorantMetrics(systemName))
	else:
		entities = dataUtils.getCandidateFeatureEnvy(systemName)
		metrics.append(dataUtils.getFEHistMetrics(systemName))
		metrics.append(dataUtils.getFEInCodeMetrics(systemName))
		metrics.append(dataUtils.getFEJDeodorantMetrics(systemName))


	instances = []
	for entity in entities:
		instance = []
		for metricMap in metrics:
			instance += metricMap[entity]
		instances.append(instance)
	instances = np.array(instances).astype(float)

	# Batch normalization
	'''if normalized:
		scaler = StandardScaler()
		scaler.fit(instances)
		return scaler.transform(instances)'''

	scaler = StandardScaler()
	scaler.fit(instances)
	instances = scaler.transform(instances)

	instances = np.concatenate((instances, np.tile(getSystemConstants(systemName), (instances.shape[0],1))), axis=1)

	return instances


def getSystemConstants(systemName):
	systemToIndexMap = {
		'android-frameworks-opt-telephony': 0,
		'android-platform-support': 1,
		'apache-ant': 2,
		'apache-tomcat': 3,
		'lucene': 4,
		'argouml': 5,
		'jedit': 6,
		'xerces-2_7_0': 7
	}

	# Sizes of the systems (i.e, number of classes)
	sizes = [190, 104, 755, 1005, 160, 1246, 437, 658]

	# History length of the systems (i.e, number of commits)
	nb_commit = [98, 195, 6397, 3289, 429, 5559, 1181, 3453]

	constants = np.array([[sizes[i], nb_commit[i]] for i in range(8)]).astype(float)

	# Normalization
	scaler = StandardScaler()
	scaler.fit(constants)

	if systemName in systemToIndexMap:
		rescaledConstants = scaler.transform(constants)
		return rescaledConstants[systemToIndexMap[systemName]]
	else:
		size = len(dataUtils.getAllClasses(systemName))
		history_length = len(dataUtils.getHistory(systemName, 'C'))
		rescaledConstants = scaler.transform([[size, history_length]])
		return rescaledConstants[0] 
