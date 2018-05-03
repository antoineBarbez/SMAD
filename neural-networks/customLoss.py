from __future__ import division

import tensorflow as tf

''' Differentiable approximation of the f-measure performed by the model on a batch.
    Based on the article of Martin Jansche "Maximum Expected F-Measure Training of Logistic Regression Models"

    true_positive -> sum(sigmoid(gamma*logits)) for label = +1
    detected -> sum(sigmoid(gamma*logits))

    for gamma -> + infinity
'''
def f_measure_approx(logits, labels, gamma):
    param = tf.constant([1,0], tf.float32, shape=[1,2])
    true_positive = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.multiply(labels, tf.nn.softmax(gamma*logits)), 0, keep_dims=True), transpose_b=True))
    positive = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(labels, 0, keep_dims=True), transpose_b=True))
    detected = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.nn.softmax(gamma*logits), 0, keep_dims=True), transpose_b=True))

    return 2*true_positive/(positive+detected)

def loss(logits, labels):
	return 1 - f_measure_approx(logits, labels, 4)