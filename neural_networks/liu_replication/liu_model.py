from context import customLoss

import tensorflow as tf


class LiuCNN(object):
	def __init__(self):
		# Placeholders for instances and labels
		self.input_names     = tf.placeholder(tf.float32,[None, 15, 200], name="input_names")
		self.input_distances = tf.placeholder(tf.float32,[None, 2], name="input_distances")
		self.input_y = tf.placeholder(tf.float32,[None, 2], name="input_y")

		# Placeholders for learning parameters
		self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
		self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
		self.beta = tf.placeholder(tf.float32, name="beta")
		self.cut_names = tf.placeholder(tf.float32, shape=(), name="cut_names")

		regularizer = tf.contrib.layers.l2_regularizer(scale=self.beta)
		init_xavier = tf.contrib.layers.xavier_initializer()
		init_zero = tf.zeros_initializer()

		# For asymmetric training
		names = tf.scalar_mul(self.cut_names, self.input_names)

		conv_names_1 = tf.layers.conv1d(names,
										128,
										1,
										padding = "same",
										activation=tf.tanh,
										kernel_regularizer=regularizer,
										kernel_initializer=init_zero)

		c1_drop_names = tf.nn.dropout(conv_names_1, self.dropout_keep_prob)

		conv_names_2 = tf.layers.conv1d(c1_drop_names,
										128,
										1,
										activation=tf.tanh,
										kernel_regularizer=regularizer,
										kernel_initializer=init_zero)
		conv_names_3 = tf.layers.conv1d(conv_names_2,
										128,
										1,
										activation=tf.tanh,
										kernel_regularizer=regularizer,
										kernel_initializer=init_zero)
		model_left = tf.contrib.layers.flatten(conv_names_3)



		distances = tf.expand_dims(self.input_distances, -1)

		conv_distances_1 = tf.layers.conv1d(distances,
											128,
											1,
											padding = "same",
											activation=tf.tanh,
											kernel_regularizer=regularizer,
											kernel_initializer=init_xavier)

		c1_drop_distances = tf.nn.dropout(conv_distances_1, self.dropout_keep_prob)

		conv_distances_2 = tf.layers.conv1d(c1_drop_distances,
											128,
											1,
											activation=tf.tanh,
											kernel_regularizer=regularizer,
											kernel_initializer=init_xavier)
		conv_distances_3 = tf.layers.conv1d(conv_distances_2,
											128,
											1,
											activation=tf.tanh,
											kernel_regularizer=regularizer,
											kernel_initializer=init_xavier)
		model_right = tf.contrib.layers.flatten(conv_distances_3)

		merge = tf.concat([model_left, model_right], 1)
		merge_drop = tf.nn.dropout(merge, self.dropout_keep_prob)
		dense = tf.layers.dense(merge_drop,
								128,
								activation=tf.tanh,
								kernel_regularizer=regularizer,
								kernel_initializer=init_xavier)
		self.logits = tf.layers.dense(dense,
										2,
										kernel_regularizer=regularizer,
										kernel_initializer=init_xavier)
		self.inference = tf.nn.softmax(self.logits)

		# Loss function
		with tf.name_scope("loss"):
			self.loss = customLoss.loss(self.logits, self.input_y)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)

