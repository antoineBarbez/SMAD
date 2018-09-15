import tensorflow as tf

class Layer(object):
	def __init__(self, input, n_in, n_out, initialization='normal', activation=tf.tanh):
		if initialization == 'normal':
			self.w = tf.Variable(tf.truncated_normal(shape=[n_in, n_out]), name="w")
			self.b = tf.Variable(tf.zeros([n_out]), name="b")

		if initialization == 'xavier':
			initializer = tf.contrib.layers.xavier_initializer()
			self.w = tf.Variable(initializer([n_in, n_out]), name="w")
			self.b = tf.Variable(initializer([n_out]), name="b")

		self.input  = input
		self.output = activation(tf.matmul(self.input,self.w) + self.b, name="activation")