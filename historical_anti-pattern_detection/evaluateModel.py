import tensorflow as tf


def true_positive(output, labels):
	tp = tf.cast(tf.equal(tf.argmax(output,1) + tf.argmax(labels,1), 0), tf.float32)

	return tp

def precision(output, labels):
	tp = true_positive(output, labels)
	detected = tf.cast(tf.equal(tf.argmax(output,1), 0), tf.float32)


	return tf.reduce_sum(tp)/tf.reduce_sum(detected)

def recall(output, labels):
	tp = true_positive(output, labels)
	positive = tf.cast(tf.equal(tf.argmax(labels,1), 0), tf.float32)


	return tf.reduce_sum(tp)/tf.reduce_sum(positive)

def f_mesure(output, labels):
	prec = precision(output, labels)
	rec = recall(output, labels)


	return 2*prec*rec/(prec+rec)

def accuracy(output, labels):
	correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(labels,1))

	return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
