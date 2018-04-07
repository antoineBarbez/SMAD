from __future__    import print_function
from model         import *
from transformData import *
from evaluateModel import *

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import math
import os
import progressbar
import random
import reader


os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

tf.reset_default_graph()

systems_names = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony', 'android-platform-support']

def generateRandomHyperParameters():
	beta = random.uniform(0, 0.4)
	learning_rate = 10**-random.uniform(0,2.5)
	nbLayer = random.randint(2,3)
	
	layers = []
	minBound = 4
	maxBound = 128
	for _ in range(nbLayer):
		nb = random.randint(minBound, maxBound)
		layers.append(nb)
		maxBound = nb

	return learning_rate, beta, layers

#Constants
num_tests = 150

num_steps = 400
num_networks = 5
input_size = 4
output_size = 2

# Create datasets
systems_instances = []
systems_labels    = []
for systemName in systems_names:
	x, y = reader.getAdvisorsBlobData(systemName)
	systems_instances.append(x)
	systems_labels.append(y)


# To save and restore a trained model
#saver = tf.train.Saver()

def evalModel(learning_rate, beta, layers):
	p_x = tf.placeholder(tf.float32,[None, input_size])
	p_y = tf.placeholder(tf.float32,[None, output_size])

	model = Model(p_x, p_y, layers, learning_rate, beta)
	session = tf.Session()

	results = []
	for i in range(len(systems_instances)):
		x_train = list(systems_instances)
		y_train = list(systems_labels)

		x_valid = x_train.pop(i)
		y_valid = y_train.pop(i)

		# Initialization and trainning
		session.run(tf.global_variables_initializer())
		for step in range(num_steps):
			for i in range(len(x_train)):
				batch_x, batch_y = shuffle(x_train[i] ,  y_train[i])
				feed_dict_train = {p_x: batch_x, p_y: batch_y}

				session.run(model.learning_step, feed_dict=feed_dict_train)

		feed_dict_valid = {p_x: x_valid}
		pred = session.run(model.inference, feed_dict=feed_dict_valid)
		p = precision(pred, y_valid).eval(session=session)
		r = recall(pred, y_valid).eval(session=session)
		f = 2*p*r/(p+r) if p+r != 0 else 0
		#print(str(p) + ' ' + str(r) + ' ' + str(f))

		results.append([p, r, f])

	return np.mean(np.array(results), axis=0)

count = 0
bar = progressbar.ProgressBar(maxval=num_tests, \
	widgets=['Performing cross validation: ' ,progressbar.Percentage()])
bar.start()
	
F = open('cross-validation_results.csv', 'w')
F.write("Learning rate;Beta;Layers;Precision;Recall;F-mesure\n")

params = []
perfs  = []
for i in range(num_tests):
	learning_rate, beta, layers = generateRandomHyperParameters()
	results = evalModel(learning_rate, beta, layers)
	params.append([learning_rate, beta, layers])
	perfs.append(results)
	bar.update(i)

args = np.argsort(np.array(perfs), axis=0)
bar.finish()

for i in reversed(range(num_tests)):
	i = args[i][2]
	F.write(str(params[i][0]) + ';' + str(params[i][1]) + ';' + str(params[i][2]) + ';' + str(perfs[i][0]).replace(",", "") + ';' + str(perfs[i][1]) + ';' + str(perfs[i][2]) + '\n')

F.close()


		



