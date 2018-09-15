import mergedDetection as md
import numpy           as np
import tensorflow      as tf

import csv
import os
import sys

sys.path.insert(0, '../../')
import reader


# This script uses the pre-trained mergedDetection networks to detect Blobs in systems and 
# create training instances for convHIST.


def get_save_path(net_number):
	save_dir = "./trained_models/final/"
	return save_dir + 'network' + str(net_number)


# Returns the Bayesian averaging between all network's prediction
def ensemble_predictions(model, session, x):
	predictions = []
	for i in range(num_networks):
		# Reload the variables into the TensorFlow graph.
		saver.restore(sess=session, save_path=get_save_path(i))

		#Perform forward calculation
		feed_dict_valid = {model.input_x: x, model.dropout_keep_prob:1.0}
		pred = session.run(model.inference, feed_dict=feed_dict_valid)
		predictions.append(pred)
  	
  	return np.mean(np.array(predictions), axis=0)


if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

	trainning_systems = ['apache-derby',
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

	# Constants
	layers = [78, 28]
	num_networks = 5

	# Create dataset
	x_input = []
	for systemName in trainning_systems:
		print(systemName)
		x = reader.getMDBlobInstances(systemName)
		x_input.append(x)

	# Create model
	model = md.MergedDetection(layers)

	# To save and restore a trained model
	saver = tf.train.Saver()

	session = tf.Session()

	for i in range(len(x_input)):
		classFile = '../../data/instances/classes/' + trainning_systems[i] + '.csv'
		labelFile = '../../data/labels/Blob/generated/' + trainning_systems[i] + '.csv'

		# Get all the classes in the system 
		classes = []
		with open(classFile, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')

			for row in reader:
				classes.append(row[0])

		# Get the ensemnle prediction
		output = ensemble_predictions(model, session, x_input[i])

		# Get the indexes of affected classes
		blobIndex = np.where(output[:,0]>0.5)

		F = open(labelFile, 'w')
		for index in blobIndex[0]:
			F.write(classes[index] + '\n')
		F.close()