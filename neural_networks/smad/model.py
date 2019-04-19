from context import customLoss

import tensorflow as tf


class SMAD(object):
	def __init__(self, shape, input_size):

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, input_size], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, 2], name="input_y")
		
		# Placeholders for learning parameters
		self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
		self.beta              = tf.placeholder(tf.float32, name="beta")

		# L2 regularization & initialization
		l2_reg = tf.contrib.layers.l2_regularizer(scale=self.beta)
		xavier = tf.contrib.layers.xavier_initializer()

		# Hidden layers
		h_in = self.input_x
		for size in shape:
			with tf.name_scope("hidden-%s" % size):
				h_in = tf.layers.dense(h_in,
									size,
									activation=tf.tanh,
									kernel_initializer=xavier,
									kernel_regularizer=l2_reg,
									bias_regularizer=l2_reg)

		# Output layer
		with tf.name_scope("output"):
			self.logits = tf.layers.dense(h_in,
										2,
										kernel_initializer=xavier,
										kernel_regularizer=l2_reg,
										bias_regularizer=l2_reg)
			self.inference = tf.nn.softmax(self.logits)

		# Loss function
		with tf.name_scope("loss"):
			self.loss = customLoss.loss(self.logits, self.input_y)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)
