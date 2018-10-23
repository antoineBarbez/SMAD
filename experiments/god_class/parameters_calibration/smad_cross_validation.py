from context import ROOT_DIR, md, nnUtils

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import math
import os
import progressbar
import random



def generateRandomHyperParameters():
	beta = 10**-random.uniform(0.0, 2.5)
	learning_rate = 10**-random.uniform(0.0, 2.5)
	nbLayer = random.randint(2,3)
	dropout = random.randint(5, 10)*0.1
	
	layers = []
	minBound = 4
	maxBound = 140
	for _ in range(nbLayer):
		nb = random.randint(minBound, maxBound)
		layers.append(nb)
		maxBound = nb

	return learning_rate, beta, layers, dropout



# Train and evaluate
def optimize(learning_rate, beta, layers, dropout):
	# New graph
	tf.reset_default_graph()

	# Create model
	model = md.SMAD(layers, input_size, constants_size)
	session = tf.Session()

	# Ensemble prediction
	predictions = []
	# For each of the neural networks.
	for _ in range(num_networks):
		# Initialize the variables of the TensorFlow graph.
		session.run(tf.global_variables_initializer())

		for step in range(num_steps):
			#Imballanced batch trainning
			for i in range(len(x_train)):
				constants, batch_x, batch_y = c_train[i], x_train[i], y_train[i]
				feed_dict_train = {
							model.input_x: batch_x,
							model.input_y: batch_y,
							model.constants: constants,
							model.dropout_keep_prob:dropout,
							model.learning_rate:learning_rate,
							model.beta:beta}

				session.run(model.learning_step, feed_dict=feed_dict_train)

		#Perform forward calculation
		feed_dict_valid = {model.input_x: x_test, model.constants: c_test, model.dropout_keep_prob:1.0}
		pred = session.run(model.inference, feed_dict=feed_dict_valid)
		predictions.append(pred)
  	
  	output = np.mean(np.array(predictions), axis=0)
	result = nnUtils.f_measure(output, y_test).eval(session=session)

	session.close()
	return result
			

if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

	validation_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']

	#Constants
	num_tests      = 300
	num_steps      = 100
	num_networks   = 1

	input_size     = 6
	constants_size = 2
	output_size    = 2

		
	x_valid = []
	c_valid = []
	y_valid = []
	for systemName in validation_systems:
		x = nnUtils.getInstances(systemName, 'god_class')
		y = nnUtils.getLabels(systemName, 'god_class')
		c = nnUtils.getSystemConstants(systemName)
		x_valid.append(x)
		y_valid.append(y)
		c_valid.append(c)



	bar = progressbar.ProgressBar(maxval=num_tests, \
		widgets=['Performing cross validation: ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments/god_class/parameters_calibration/outputs/cv_results.csv')


	params = []
	perfs  = []
	for i in range(num_tests):
		learning_rate, beta, layers, dropout = generateRandomHyperParameters()
		params.append([learning_rate, beta, layers, dropout])
		f_measures = []
		for j in range(len(validation_systems)):
			x_train = list(x_valid)
			c_train = list(c_valid)
			y_train = list(y_valid)

			x_test = x_train.pop(j)
			c_test = c_train.pop(j)
			y_test = y_train.pop(j)

			f_m = optimize(learning_rate, beta, layers, dropout)
			if math.isnan(f_m):
				f_m = 0.0
			f_measures.append(f_m)
		perfs.append(np.mean(np.array(f_measures)))
		args = np.argsort(np.array(perfs))

		F = open(output_file_path, 'w')
		F.write("Learning rate;Beta;Layers;Dropout;F-mesure\n")
		for k in reversed(args):
			F.write(str(params[k][0]) + ';' + str(params[k][1]) + ';' + str(params[k][2]) + ';' + str(params[k][3]) + ';' + str(perfs[k]) + '\n')
		F.close()
		bar.update(i+1)

	bar.finish()