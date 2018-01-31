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

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'


tf.reset_default_graph()

#constants
starter_learning_rate = 0.26
beta = 0.0
layers = [32,16,8]
num_steps = 1000

# Create datasets
instances , labels = reader.constructDataset2()
dataset_x , dataset_y = shuffle(instances , labels)
dataset_x = standardizeData(dataset_x)

validSet_start_idx = int(math.ceil(len(dataset_x)*0.7))

x_train = dataset_x[:validSet_start_idx,:]
y_train = dataset_y[:validSet_start_idx,:]
x_valid = dataset_x[validSet_start_idx:,:]
y_valid = dataset_y[validSet_start_idx:,:]


# Print datasets repartition of occurences
nonZeroTotal = np.nonzero(dataset_y[:,0])[0].size
nonZeroTrain = np.nonzero(y_train[:,0])[0].size
nonZeroValid = np.nonzero(y_valid[:,0])[0].size

print('nonzero :', nonZeroTotal, nonZeroTrain, nonZeroValid)


# Create model
input_size = len(x_train[0])
output_size = len(y_train[0])

p_x = tf.placeholder(tf.float32,[None, input_size])
p_y = tf.placeholder(tf.float32,[None, output_size])

model = Model(p_x, p_y)

# To save and restore a trained model
saver = tf.train.Saver()

losses_train = []
losses_valid = []
bestLossStep = 0
bestLoss = 100
with tf.Session() as session:
	session.run(tf.global_variables_initializer())

	feed_dict_train = {p_x: x_train, p_y: y_train}
	feed_dict_valid = {p_x: x_valid, p_y: y_valid}

	for step in range(num_steps):

		session.run(model.learning_step, feed_dict=feed_dict_train)

		l_train = session.run(model.loss, feed_dict=feed_dict_train)
		l_valid = session.run(model.loss, feed_dict=feed_dict_valid)
		losses_train.append(l_train)
		losses_valid.append(l_valid)

		if l_valid < bestLoss:
			bestLoss = l_valid
			bestLossStep = step

	# Save the model
	save_path = saver.save(session, "./data/trained_models/model", global_step=num_steps)
  	print("Model saved in path: %s" % save_path)

  	# Evaluate the model on the validation set
	output = session.run(model.inference, feed_dict=feed_dict_valid)
	#precision, recall, f_mesure, accuracy = evaluate_model(output, y_valid)
	pre = precision(output, y_valid)
	rec = recall(output, y_valid)
	f_m = f_mesure(output, y_valid)
	acc = accuracy(output, y_valid)

	print('\n')
	print('Precision :', "{0:.3f}".format(pre.eval()))
	print('Recall :', "{0:.3f}".format(rec.eval()))
	print('F-Mesure :', "{0:.3f}".format(f_m.eval()))
	print('Accuracy :', "{0:.3f}".format(acc.eval()))
	print('\n')
	print('Best loss :',"{0:.3f}".format(bestLoss),' at step :',bestLossStep)

	plt.plot(range(num_steps), losses_train, range(num_steps), losses_valid)
	plt.show()

