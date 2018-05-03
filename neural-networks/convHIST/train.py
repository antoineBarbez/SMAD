import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import convHIST
import math
import os
import sys

sys.path.insert(0, '../')
from evaluateModel import *
from transformData import *

sys.path.insert(0, '../../')
import reader


def get_save_path(net_number):
	save_dir = "./trained_models/train/"
	return save_dir + 'network' + str(net_number)


#Performs training on the current model
def optimize():
	learning_rate = starter_learning_rate

	learning_rates = []
	losses_train   = []
	losses_test    = []
	for step in range(num_steps):
		# Learning rate decay
		if (step%25 == 0) & (step>1):
			learning_rate = learning_rate*0.2

		learning_rates.append(learning_rate*100)

		#Imballanced batch trainning
		l_train = []
		x_t, y_t = shuffle(x_train, y_train)
		for i in range(len(x_t)):
			batch_x, batch_y = shuffle(x_t[i], y_t[i])
			feed_dict_train = {
						model.input_x: batch_x,
						model.input_y: batch_y,
						model.dropout_keep_prob:dropout,
						model.learning_rate:learning_rate,
						model.beta:beta}

			session.run(model.learning_step, feed_dict=feed_dict_train)

			l = session.run(model.loss, feed_dict=feed_dict_train)
			l_train.append(l)

		l_test = []
		for i in range(len(x_test)):
			feed_dict_valid = {
						model.input_x: x_test[i],
						model.input_y: y_test[i],
						model.dropout_keep_prob:1.0,
						model.beta:beta}

			l = session.run(model.loss, feed_dict=feed_dict_valid)
			print("Step-" + str(step) + ": " + str(l))
			l_test.append(l)

		mean_l_train = np.mean(np.array(l_train))
		mean_l_test = np.mean(np.array(l_test))
		losses_train.append(mean_l_train)
		losses_test.append(mean_l_test)

	return learning_rates, losses_train, losses_test



if __name__ == "__main__":

	tf.reset_default_graph()

	trainning_systems = [
                    'apache-derby',
                    'apache-log4j1',
                    'apache-log4j2',
                    'apache-velocity',
                    'javacc',
                    'jena',
                    'jgraphx',
                    'jgroups',
                    'jhotdraw',
                    'jspwiki',
                    'junit',
                    'mongodb',
                    'pmd']


	validation_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']

	test_systems = ['apache-tomcat', 'jedit', 'android-platform-support']


	#constants
	starter_learning_rate = 0.0001
	beta                  = 0.001
	dropout               = 0.5
	filter_sizes          = [3, 7, 17]
	num_filters           = 20
	fc_layers             = [100, 30]

	num_steps = 100

	# Create datasets
x_train = []
y_train = []
for systemName in trainning_systems:
	x = reader.getBlobInstances(systemName)
	x_train.append(x)
	y_train.append(reader.getBlobLabels(systemName, 'generated'))

for systemName in validation_systems:
	x = reader.getBlobInstances(systemName)
	x_train.append(x)
	y_train.append(reader.getBlobLabels(systemName, 'hand_validated')) 
 
    
x_test = []
y_test = []
for systemName in test_systems:
	x = reader.getBlobInstances(systemName)
	x_test.append(x)
	y_test.append(reader.getBlobLabels(systemName, 'hand_validated'))


	# Create model
	model = convHIST.convHist(filter_sizes, num_filters, fc_layers)

	# To save and restore a trained model
	saver = tf.train.Saver()

	session = tf.Session()

	session.run(tf.global_variables_initializer())

	learning_rates, losses_train, losses_test = optimize()

	# Save the optimized variables to disk.
	saver.save(sess=session, save_path=get_save_path(i))


	# Evaluate the model on the test set
	pre = []
	rec = []
	f_m = []
	acc = []
	for i in range(len(x_test)):
		feed_dict_test = {model.input_x: x_test[i], model.dropout_keep_prob:1.0}
		output = session.run(model.inference, feed_dict=feed_dict_test)
		p = precision(output, y_test[i]).eval(session=session)
		r = recall(output, y_test[i]).eval(session=session)
		f = f_mesure(output, y_test[i]).eval(session=session)
		a = accuracy(output, y_test[i]).eval(session=session)

		print(test_systems[i])
		print('P :' + str(p))
		print('R :' + str(r))
		print('F :' + str(f))
		print('A :' + str(a))
		print('')
			
		pre.append(p)
		rec.append(r)
		f_m.append(f)
		acc.append(a)

	session.close()

	print('')
	print('MEAN')
	print('Precision :' + str(np.mean(np.array(pre))))
	print('Recall    :' + str(np.mean(np.array(rec))))
	print('F-Mesure  :' + str(np.mean(np.array(f_m))))
	print('Accuracy  :' + str(np.mean(np.array(acc))))
	print('')

	plt.plot(range(num_steps), np.array(losses_train), range(num_steps), np.array(losses_test), range(num_steps), l_r)
	plt.show()

