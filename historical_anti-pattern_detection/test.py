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


systems = [
	'android-frameworks-opt-telephony',
	'android-frameworks-sdk',
	'android-frameworks-tool-base',
	'android-platform-support',
	'apache-ant',
	'apache-cassandra',
	'apache-commons-codec',
	'apache-commons-io',
	'apache-commons-lang',
	'apache-commons-logging',
	'apache-derby',
	'apache-ivy',
	'apache-karaf',
	'apache-log4j',
	'apache-pig',
	'apache-struts',
	'apache-tomcat',
	'eclipse-jdt-core',
	'google-guava',
	'jedit',
	'mongodb'
]


p_x = tf.placeholder(tf.float32,[None, 4])
p_y = tf.placeholder(tf.float32,[None, 2])

model = Model(p_x, p_y)

# To save and restore a trained model
saver = tf.train.Saver()


with tf.Session() as session:

	saver.restore(session, "./data/trained_models/model-1000")
	print("Model restored.")

	F = open("results.txt", 'a')

	for system in systems:
		print(system)

		x_test, y_test = reader.system2Data(system)
		x_test = standardizeData(x_test)

		output = session.run(model.inference, feed_dict={p_x: x_test, p_y: y_test})

		pre = precision(output, y_test)
		rec = recall(output, y_test)
		f_m = f_mesure(output, y_test)

		F.write(str(system) + " : "+ "{0:.3f}".format(pre.eval()) + " " + "{0:.3f}".format(rec.eval()) + " " + "{0:.3f}".format(f_m.eval()) + "\n")
	
	F.close()
