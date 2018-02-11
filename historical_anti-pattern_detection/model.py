
from __future__ import division
from __future__ import print_function

import tensorflow as tf

class Layer(object):
	def __init__(self, input, n_in, n_out, activation=tf.tanh):
		self.w = tf.Variable(tf.truncated_normal(shape=[n_in, n_out]))
		self.b = tf.Variable(tf.zeros([n_out]))

		self.input = input
		self.output = activation(tf.matmul(self.input,self.w) + self.b)


class Model(object):
	def __init__(self, instances, labels=None, shape=[32,16,8], starter_learning_rate=0.26, beta=0):
		self.instances = instances
		self.labels = labels

		self.input_size = 4
		self.output_size = 2
		self.shape = shape
		self.shape.append(self.output_size)

		# Construct the model
		h = self.instances
		n_in = self.input_size
		self.L2 = 0
		self.layers = []
		for size in self.shape:
			layer = Layer(h, n_in, size)
			self.logits = tf.matmul(layer.input,layer.w)
			self.L2 += tf.nn.l2_loss(layer.w)
			self.layers.append(layer)
			h = layer.output
			n_in = size


		# Loss function
		self.loss = 1 - f_mesure_approx(self.logits, self.labels, 2)
		self.loss = tf.reduce_mean(self.loss + beta * self.L2)

		# Learning mecanism with learning rate decay
		self.global_step = tf.Variable(0, trainable=False)
		self.learning_rate = tf.train.exponential_decay(
			starter_learning_rate,
			self.global_step,
			100,
			0.9,
			staircase=True)

		self.learning_step = (
            tf.train.GradientDescentOptimizer(self.learning_rate)
            .minimize(self.loss, global_step=self.global_step)
        )

		# Forward calculation
		self.inference = tf.nn.softmax(self.logits)


''' Differentiable approximation of the f-mesure performed by the model on a given dataset.
    Based on the article of Martin Jansche "Maximum Expected F-Measure Training of Logistic Regression Models"

    true_positive -> sum(sigmoid(gamma*logits)) for label = +1
    detected -> sum(sigmoid(gamma*logits))

    for gamma -> + infinity
'''
def f_mesure_approx(logits, labels, gamma):
    param = tf.constant([1,0], tf.float32,shape=[1,2])
    true_positive = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.multiply(labels,tf.nn.softmax(gamma*logits)),0,keep_dims=True),transpose_b=True))
    positive = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(labels,0,keep_dims=True),transpose_b=True))
    detected = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.nn.softmax(gamma*logits),0,keep_dims=True),transpose_b=True))

    return 2*true_positive/(positive+detected)
