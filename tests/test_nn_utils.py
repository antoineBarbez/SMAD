from context import nnUtils, dataUtils

import numpy as np
import tensorflow as tf

import math
import os
import unittest

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

class TestNNUtils(unittest.TestCase):
	def setUp(self):
		self.sess = tf.Session()
		self.set_1 = np.array([[0,1], [0,1], [0,1], [0, 1], [0, 1]])
		self.set_2 = np.array([[1,0], [1,0], [1,0], [1, 0], [1, 0]])
		self.set_3 = np.array([[0,1], [0,1], [1,0], [0, 1], [0, 1]])
		self.set_4 = np.array([[0,1], [1,0], [1,0], [1, 0], [0, 1]])
		self.set_5 = np.array([[0,1], [1,0], [0,1], [1, 0], [0, 1]])

		self.systems = [
			'android-frameworks-opt-telephony',
			'android-platform-support',
			'apache-ant',
			'apache-tomcat',
			'lucene',
			'argouml',
			'jedit',
			'xerces-2_7_0'
		] 

	def tearDown(self):
		del self.set_1
		del self.set_2
		del self.set_3
		del self.set_4
		del self.set_5
		del self.systems
		self.sess.close()


	def test_precision(self):
		self.assertTrue(math.isnan(nnUtils.precision(self.set_1, self.set_1).eval(session=self.sess)))
		self.assertTrue(math.isnan(nnUtils.precision(self.set_1, self.set_2).eval(session=self.sess)))
		self.assertAlmostEqual(nnUtils.precision(self.set_2, self.set_3).eval(session=self.sess), 0.2, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_2, self.set_4).eval(session=self.sess), 0.6, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_3, self.set_3).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_3, self.set_2).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_3, self.set_4).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_4, self.set_3).eval(session=self.sess), 0.333333, 5)
		self.assertAlmostEqual(nnUtils.precision(self.set_3, self.set_5).eval(session=self.sess), 0.0, 5)


	def test_recall(self):
		self.assertTrue(math.isnan(nnUtils.recall(self.set_1, self.set_1).eval(session=self.sess)))
		self.assertAlmostEqual(nnUtils.recall(self.set_1, self.set_2).eval(session=self.sess), 0.0, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_2, self.set_3).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_2, self.set_4).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_3, self.set_3).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_3, self.set_2).eval(session=self.sess), 0.2, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_3, self.set_4).eval(session=self.sess), 0.333333, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_4, self.set_3).eval(session=self.sess), 1.0, 5)
		self.assertAlmostEqual(nnUtils.recall(self.set_3, self.set_5).eval(session=self.sess), 0.0, 5)
	
	def test_f_measure(self):
		self.assertTrue(math.isnan(nnUtils.f_measure(self.set_1, self.set_1).eval(session=self.sess)))
		self.assertAlmostEqual(nnUtils.f_measure(self.set_3, self.set_2).eval(session=self.sess), 0.333333, 5)



	def test_get_labels_god_class(self):
		for system in self.systems:
			classes = dataUtils.getClasses(system)
			antipatterns = dataUtils.getAntipatterns(system, 'god_class')
			labels  = nnUtils.getLabels(system, 'god_class')

			self.assertEqual(len(classes), len(labels))
			self.assertEqual(len(antipatterns), len(np.where(labels[:,0]==1)[0]))

	def test_get_Instances_god_class(self):
		for system in self.systems:
			classes = dataUtils.getClasses(system)
			instances = nnUtils.getInstances(system, 'god_class')

			self.assertEqual(len(classes), len(instances))

if __name__ == '__main__':
	unittest.main()