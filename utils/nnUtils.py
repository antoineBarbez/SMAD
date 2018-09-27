from context               import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import numpy      as np
import tensorflow as tf

import dataUtils
import random
import sys

sys.path.insert(0, ROOT_DIR)
import detection_tools.confidence_metrics as cm

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
def shuffle(instances, labels):
	assert len(instances) == len(labels), 'instances and labels must have the same number of elements'

	idx = range(len(instances))
	random.shuffle(idx)

	x = np.array([instances[i] for i in idx])
	y = np.array([labels[i] for i in idx])
	
	return x, y


### INSTANCES AND LABELS GETTERS ###

# Get labels in vector form for a given system
# antipattern in ['god_class', 'feature_envy']
def getLabels(systemName, antipattern):
	true = dataUtils.getAntipatterns(systemName, antipattern)

	if antipattern == 'god_class':
		entities = dataUtils.getClasses(systemName)
	else:
		entities = []

	labels = []
	for entity in entities:
		if entity in true:
			labels.append([1, 0])
		else:
			labels.append([0, 1])

	return np.array(labels)


# Number of class per system
systems_sizes = {
	'android-frameworks-opt-telephony': 190,
	'android-platform-support': 104,
	'apache-ant': 755,
	'apache-tomcat': 1005,
	'lucene': 160,
	'argouml': 1246,
	'jedit': 437,
	'xerces-2_7_0': 658
}

def getGodClassInstances(systemName):
	classes = dataUtils.getClasses(systemName)

	classToHistGCCM       = cm.getHistGCCM(systemName)
	classToDecorGCCM      = cm.getDecorGCCM(systemName)
	classToJDeodorantGCCM = cm.getJDeodorantGCCM(systemName)

	instances = []
	for klass in classes:
		instance = []
		instance.append(classToHistGCCM[klass])
		instance.append(classToDecorGCCM[klass])
		instance.append(classToJDeodorantGCCM[klass])

		instances.append(instance)

	instances = np.array(instances).astype(float)

	# Batch normalization
	scaler = StandardScaler()
	scaler.fit(instances)
	rescaledInstances = scaler.transform(instances)

	return rescaledInstances