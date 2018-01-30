import tensorflow as tf
import transformData as td
import numpy as np
import matplotlib.pyplot as plt

import reader
import math

from model import *


tf.reset_default_graph()


def evaluate_model(output, labels):
    true_positive = tf.cast(tf.equal(tf.argmax(output,1) + tf.argmax(labels,1), 0), tf.float32)
    positive = tf.cast(tf.equal(tf.argmax(labels,1), 0), tf.float32)
    detected = tf.cast(tf.equal(tf.argmax(output,1), 0), tf.float32)
    correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(labels,1))

    precision = tf.reduce_sum(true_positive)/tf.reduce_sum(detected)
    recall = tf.reduce_sum(true_positive)/tf.reduce_sum(positive)
    f_mesure = 2*precision*recall/(precision+recall)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    return precision, recall, f_mesure, accuracy
    

#constants
starter_learning_rate = 0.26
beta = 0.0
layers = [32,16,8]
num_steps = 1000

# Create datasets
instances , labels = reader.constructDataset2()
dataset_x , dataset_y = td.shuffle(instances , labels)
dataset_x = td.standardizeData(dataset_x)

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

losses_train = []
losses_valid = []
#fm = []
#lrates = []
bestLossStep = 0
bestLoss = 100
#bestFMStep = 0
#bestFM = 0
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

	output = session.run(model.inference, feed_dict=feed_dict_valid)
	precision, recall, f_mesure, accuracy = evaluate_model(output, y_valid)

	print('Precision :', precision.eval())
	print('Recall :', recall.eval())
	print('F-Mesure :', f_mesure.eval())
	print('Accuracy :', accuracy.eval())
	print('\n')
	print('Best loss :',bestLoss,' at step :',bestLossStep)

	plt.plot(range(num_steps), losses_train, range(num_steps), losses_valid)
	plt.show()

