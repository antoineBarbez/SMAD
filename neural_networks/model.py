import tensorflow as tf

import customLoss
import fullyConnectedLayer



class MergedDetection(object):
	def __init__(self, shape, input_size=4):
		output_size = 2

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, input_size], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, output_size], name="input_y")
		
		# Placeholders for learning parameters
		self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
		self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
		self.beta              = tf.placeholder(tf.float32, name="beta")


		# L2 loss
		L2_norm = tf.constant(0.0)

		# Construct the model
		with tf.name_scope("dropout"):
			h_drop = tf.nn.dropout(self.input_x, self.dropout_keep_prob)

		h_in = h_drop
		n_in = input_size
		for size in shape:
			with tf.name_scope("hidden-%s" % size):
				layer = fullyConnectedLayer.Layer(h_in, n_in, size)
				h_in  = layer.output
				n_in  = size

				L2_norm += tf.nn.l2_loss(layer.w)
				L2_norm += tf.nn.l2_loss(layer.b) 
	
		# Output layer
		with tf.name_scope("output"):
			outputLayer = fullyConnectedLayer.Layer(h_in, n_in, output_size, initialization="normal", activation=tf.nn.softmax)
			L2_norm += tf.nn.l2_loss(outputLayer.w)
			L2_norm += tf.nn.l2_loss(outputLayer.b)

			# Forward calculation
			self.logits = tf.nn.xw_plus_b(outputLayer.input, outputLayer.w, outputLayer.b, name="logits")
			self.inference = outputLayer.output


		# Loss function
		with tf.name_scope("loss"):
			self.loss = customLoss.loss(self.logits, self.input_y) + self.beta * L2_norm


		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.loss)
