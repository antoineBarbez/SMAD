from context               import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import numpy             as np
import tensorflow        as tf
import matplotlib.pyplot as plt

import ast
import csv
import dataUtils
import os
import random
import sys

### EVALUATION ####
def detected(output):
	return np.sum((output > 0.5).astype(float))

def positive(labels):
	return np.sum(labels)

def true_positive(output, labels):
	return np.sum((output + labels > 1.5).astype(float))

def precision(output, labels):
	return true_positive(output, labels)/detected(output)

def recall(output, labels):
	return true_positive(output, labels)/positive(labels)

def f_measure(output, labels):
	p = precision(output, labels)
	r = recall(output, labels)

	return 2*p*r/(p+r)

def mcc(output, labels):
	'''
	Matthew's Correlation Coefficient
	'''
	N = labels.size
	N_pos = positive(labels)
	M_pos = detected(output)
	TP = true_positive(output, labels)

	return (TP*N - N_pos*M_pos)/(N_pos*M_pos*(N-N_pos)*(N-M_pos))**0.5

### UTILS ###

def build_dataset(antipattern, systems, normalized=True):
	input_size = {'god_class':6, 'feature_envy':7}
	X = np.empty(shape=[0, input_size[antipattern]])
	Y = np.empty(shape=[0, 1])
	for systemName in systems:
		X = np.concatenate((X, getInstances(antipattern, systemName, normalized)), axis=0)
		Y = np.concatenate((Y, getLabels(antipattern, systemName)), axis=0)

	return X, Y

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

# Returns a training and a testing dataset from an input dataset (instances and labels)
# The input dataset is first split into n_folds folds.
# The test dataset is the fold of index fold_index
# The training dataset is obtained by concatenating the n_folds-1 remaining folds. 
# X         : instances
# Y         : labels
# fold_index: the index of the fold we want to be returned as the test dataset
# n_fold    : the number of folds, i.e., k for a k-fold cross-validation 
def get_cross_validation_dataset(X, Y, fold_index, n_fold):
	folds_x, folds_y = split(X, Y, n_fold)
	x_train = np.empty(shape=[0, X.shape[-1]])
	y_train = np.empty(shape=[0, 1])
	for i in range(n_fold):
		if i != fold_index:
			x_train = np.concatenate((x_train, folds_x[i]), axis=0)
			y_train = np.concatenate((y_train, folds_y[i]), axis=0)

	return x_train, y_train, folds_x[fold_index], folds_y[fold_index]

def get_optimal_hyperparameters(tuning_file):
	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['MCC'] != 'nan':
				return {key:ast.literal_eval(row[key]) for key in row}

# Get the path of a trained model for a given approach (smad or asci)
def get_save_path(approach, antipattern, test_system, model_number):
	directory = os.path.join(ROOT_DIR, 'approaches', approach, 'trained_models', antipattern, test_system)
	if not os.path.exists(directory):
			os.makedirs(directory)
	return os.path.join(directory, 'model_' + str(model_number))

# Plot learning curves with mean and standard deviations
# losses_train: a list of lists which contain losses values for training
# losses_test : same for testing
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

# Returns an array of predictions for each input instances from a set of smells
# i.e., the set of occurrences detected by an approach.
# smells: a set of entities' names (i.e., those that have been detected) 
def predictFromDetect(antipattern, systemName, smells):
	entities = dataUtils.getEntities(antipattern, systemName)

	prediction = []
	for entity in entities:
		if entity in smells:
			prediction.append([1.])
		else:
			prediction.append([0.])

	return np.array(prediction)

def detectFromPredict(antipattern, systemName, prediction):
	entities = dataUtils.getEntities(antipattern, systemName)

	return [entities[i] for i in range(len(entities)) if prediction[i]>0.5]

# Shuffle identically several arrays
def shuffle(X, *args):
	for arg in args:
		assert len(X) == len(arg), 'all arrays to be shuffled must have the same number of elements'

	idx = range(len(X))
	random.shuffle(idx)

	output = [np.array([X[i] for i in idx])]
	for arg in args:
		output.append(np.array([arg[i] for i in idx]))
	
	return tuple(output)

def split(X, Y, nb_split):
	assert len(X) == len(Y), 'X and Y must have the same number of elements' 
	
	length = len(X)//nb_split
	sections  = [(i+1)*length for i in range(nb_split-1)]

	return np.split(X, sections), np.split(Y, sections)


### INSTANCES AND LABELS GETTERS ###

# Get labels in vector form for a given system
# antipattern in ['god_class', 'feature_envy']
def getLabels(antipattern, systemName):
	entities = dataUtils.getEntities(antipattern, systemName)
	true = dataUtils.getAntipatterns(antipattern, systemName)

	labels = []
	for entity in entities:
		if entity in true:
			labels.append([1.])
		else:
			labels.append([0.])

	return np.array(labels)


def getInstances(antipattern, systemName, normalized=True):
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
	if normalized:
		scaler = StandardScaler()
		scaler.fit(instances)
		instances = scaler.transform(instances)

	return instances
