from __future__ import division

import tensorflow as tf


class SMAD(object):
	def __init__(self, shape, input_size):

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, input_size], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, 1], name="input_y")
		
		# Placeholders for training parameters
		self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
		self.beta          = tf.placeholder(tf.float32, name="beta")
		self.gamma         = tf.placeholder(tf.float32, name="gamma")

		# L2 regularization & initialization
		l2_reg = tf.contrib.layers.l2_regularizer(scale=self.beta)
		xavier = tf.contrib.layers.xavier_initializer()

		# Hidden layers
		h_in = self.input_x
		for size in shape:
			with tf.name_scope("hidden-%s" % size):
				h_in = tf.layers.dense(
					inputs=h_in,
					units=size,
					activation=tf.tanh,
					kernel_initializer=xavier,
					kernel_regularizer=l2_reg,
					bias_regularizer=l2_reg)

		# Output layer
		with tf.name_scope("output"):
			self.logits = tf.layers.dense(
				inputs=h_in,
				units=1,
				kernel_initializer=xavier,
				kernel_regularizer=l2_reg,
				bias_regularizer=l2_reg)
			self.inference = tf.nn.sigmoid(self.logits)

		# Loss function
		with tf.name_scope("loss"):
			self.loss = 1 - mcc(self.logits, self.input_y, self.gamma)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)

def mcc(logits, labels, gamma):
	'''
	This function returns a differentiable approximation of the Matthew's Correlation
	Coefficient.

	It approximates the network's prediction as:
	floor(logits + 0.5) ~ sigmoid(gamma*logits) with gamma > 0
	'''

	N = tf.cast(tf.size(logits), tf.float32)
	N_pos = tf.reduce_sum(labels)
	M_pos = tf.reduce_sum(tf.nn.sigmoid(gamma*logits))
	TP = tf.reduce_sum(tf.multiply(labels, tf.nn.sigmoid(gamma*logits)))

	return (TP*N - N_pos*M_pos)/(N_pos*M_pos*(N-N_pos)*(N-M_pos))**0.5
