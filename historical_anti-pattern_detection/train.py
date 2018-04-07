from __future__    import print_function
from model         import *
from transformData import *
from evaluateModel import *

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import reader
import math
import os

def get_save_path(net_number):
	save_dir = "./assets/trained_models/advisors-Blob/"
	return save_dir + 'network' + str(net_number)


#Performs trainning on the current model
def optimize(model, session, x_t, y_t, x_v, y_v):
	learning_rates = []
	losses_train   = []
	losses_valid   = []
	for step in range(num_steps):
		learning_rates.append(model.learning_rate.eval(session=session))

		l_train = []
		#Imballanced batch trainning
		#x, y = shuffle(x_train , y_train)
		for i in range(len(x_t)):
			batch_x, batch_y = shuffle(x_t[i] ,  y_t[i])
			feed_dict_train = {p_x: batch_x, p_y: batch_y}

			session.run(model.learning_step, feed_dict=feed_dict_train)

			l = session.run(model.loss, feed_dict=feed_dict_train)
			l_train.append(l)

		l_valid = []
		for i in range(len(x_v)):
			feed_dict_valid = {p_x: x_v[i], p_y: y_v[i]}

			l = session.run(model.loss, feed_dict=feed_dict_valid)
			l_valid.append(l)

		mean_l_train = np.mean(np.array(l_train))
		mean_l_valid = np.mean(np.array(l_valid))
		losses_train.append(mean_l_train)
		losses_valid.append(mean_l_valid)

	return learning_rates, losses_train, losses_valid


def train_networks(model, session, x_t, y_t, x_v, y_v):
	# For each of the neural networks.
	for i in range(num_networks):
		print('Trainning the Neural Network :' + str(i))

		# Initialize the variables of the TensorFlow graph.
		session.run(tf.global_variables_initializer())

		#Begin the learning process
		learning_rates, losses_train, losses_valid = optimize(model, session, x_t, y_t, x_v, y_v)

		l_t.append(losses_train)
		l_v.append(losses_valid)
		l_r = learning_rates

	    # Save the optimized variables to disk.
		saver.save(sess=session, save_path=get_save_path(i))


#Returns the averages predicted probabilities between all the neural networks
def ensemble_predictions(model, session, x):
	predictions = []
	for i in range(num_networks):
		# Reload the variables into the TensorFlow graph.
		saver.restore(sess=session, save_path=get_save_path(i))

		#Perform forward calculation
		feed_dict_valid = {p_x: x}
		pred = session.run(model.inference, feed_dict=feed_dict_valid)
		predictions.append(pred)
  	
  	return np.mean(np.array(predictions), axis=0)


if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

	trainning_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']
	validation_systems = ['apache-tomcat', 'jedit', 'android-platform-support']

	#constants
	starter_learning_rate = 0.017
	beta = 0.103
	layers = [103, 66]
	num_steps = 400
	num_networks = 5

	# Create datasets
	x_train = []
	y_train = []
	for systemName in trainning_systems:
		x, y = reader.getAdvisorsBlobData(systemName)
		x_train.append(x)
		y_train.append(y)

	x_valid = []
	y_valid = []
	for systemName in validation_systems:
		x, y = reader.getAdvisorsBlobData(systemName)
		x_valid.append(x)
		y_valid.append(y)


	# Create model
	input_size = 4
	output_size = 2

	p_x = tf.placeholder(tf.float32,[None, input_size])
	p_y = tf.placeholder(tf.float32,[None, output_size])

	model = Model(p_x, p_y, layers, starter_learning_rate, beta)

	# To save and restore a trained model
	saver = tf.train.Saver()

	session = tf.Session()

	l_t = []
	l_v = []
	l_r = []

	#train_networks(model, session, x_train, y_train, x_valid, y_valid)

	# For each of the neural networks.
	for i in range(num_networks):
		print('Trainning the Neural Network :' + str(i))

		# Initialize the variables of the TensorFlow graph.
		session.run(tf.global_variables_initializer())

		#Begin the learning process
		learning_rates, losses_train, losses_valid = optimize(model, session, x_train, y_train, x_valid, y_valid)

		l_t.append(losses_train)
		l_v.append(losses_valid)
		l_r = learning_rates

	    # Save the optimized variables to disk.
		saver.save(sess=session, save_path=get_save_path(i))

	# Evaluate the ensemble model on the validation set
	pre = []
	rec = []
	f_m = []
	acc = []
	for i in range(len(x_valid)):
		output = ensemble_predictions(model, session, x_valid[i])
		p = precision(output, y_valid[i]).eval(session=session)
		r = recall(output, y_valid[i]).eval(session=session)
		f = f_mesure(output, y_valid[i]).eval(session=session)
		a = accuracy(output, y_valid[i]).eval(session=session)

		print('P :' + str(p))
		print('R :' + str(r))
		print('F :' + str(f))
		print()
			
		pre.append(p)
		rec.append(r)
		f_m.append(f)
		acc.append(a)

	session.close()

	print()

	print('Precision :' + str(np.mean(np.array(pre))))
	print('Recall    :' + str(np.mean(np.array(rec))))
	print('F-Mesure  :' + str(np.mean(np.array(f_m))))
	print('Accuracy  :' + str(np.mean(np.array(acc))))
	print()
	#print('Best loss :',"{0:.3f}".format(bestLoss),' at step :',bestLossStep)

	plt.plot(range(num_steps), np.mean(np.array(l_t), axis=0), range(num_steps), np.mean(np.array(l_v), axis=0), range(num_steps), l_r)
	plt.show()

