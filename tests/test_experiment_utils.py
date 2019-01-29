from context import experimentUtils, dataUtils

import numpy as np

import math
import unittest

class TestExperimentUtils(unittest.TestCase):
	def setUp(self):
		self.set_1 = ['a','b','c','d', 'e']
		self.set_2 = ['b','e', 'f', 'g']
		self.set_3 = ['c']
		self.set_4 = []

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
		del self.systems


	def test_precision(self):
		self.assertEqual(experimentUtils.precision(self.set_1, self.set_1), 1.0)
		self.assertEqual(experimentUtils.precision(self.set_1, self.set_2), 0.4)
		self.assertEqual(experimentUtils.precision(self.set_1, self.set_3), 0.2)
		self.assertEqual(experimentUtils.precision(self.set_1, self.set_4), 0.0)
		self.assertEqual(experimentUtils.precision(self.set_2, self.set_1), 0.5)
		self.assertEqual(experimentUtils.precision(self.set_2, self.set_2), 1.0)
		self.assertEqual(experimentUtils.precision(self.set_2, self.set_3), 0.0)
		self.assertEqual(experimentUtils.precision(self.set_3, self.set_1), 1.0)
		self.assertEqual(experimentUtils.precision(self.set_3, self.set_4), 0.0)
		self.assertEqual(experimentUtils.precision(self.set_4, self.set_1), 0.0)
		self.assertEqual(experimentUtils.precision(self.set_4, self.set_3), 0.0)
		self.assertEqual(experimentUtils.precision(self.set_4, self.set_4), 0.0)

	def test_recall(self):
		self.assertEqual(experimentUtils.recall(self.set_1, self.set_1), 1.0)
		self.assertEqual(experimentUtils.recall(self.set_1, self.set_2), 0.5)
		self.assertEqual(experimentUtils.recall(self.set_1, self.set_3), 1.0)
		self.assertTrue(math.isnan(experimentUtils.recall(self.set_1, self.set_4)))
		self.assertEqual(experimentUtils.recall(self.set_2, self.set_1), 0.4)
		self.assertEqual(experimentUtils.recall(self.set_2, self.set_2), 1.0)
		self.assertEqual(experimentUtils.recall(self.set_2, self.set_3), 0.0)
		self.assertEqual(experimentUtils.recall(self.set_3, self.set_1), 0.2)
		self.assertTrue(math.isnan(experimentUtils.recall(self.set_3, self.set_4)))
		self.assertEqual(experimentUtils.recall(self.set_4, self.set_1), 0.0)
		self.assertEqual(experimentUtils.recall(self.set_4, self.set_3), 0.0)
		self.assertTrue(math.isnan(experimentUtils.recall(self.set_4, self.set_4)))

	def test_f_measure(self):
		self.assertEqual(experimentUtils.f_measure(self.set_1, self.set_1), 1.0)
		self.assertEqual(experimentUtils.f_measure(self.set_1, self.set_2), 0.4444444444444445)
		self.assertEqual(experimentUtils.f_measure(self.set_1, self.set_3), 0.33333333333333337)
		self.assertTrue(math.isnan(experimentUtils.f_measure(self.set_1, self.set_4)))
		self.assertEqual(experimentUtils.f_measure(self.set_2, self.set_1), 0.4444444444444445)
		self.assertEqual(experimentUtils.f_measure(self.set_2, self.set_2), 1.0)
		self.assertEqual(experimentUtils.f_measure(self.set_2, self.set_3), 0.0)
		self.assertEqual(experimentUtils.f_measure(self.set_3, self.set_1), 0.33333333333333337)
		self.assertTrue(math.isnan(experimentUtils.f_measure(self.set_3, self.set_4)))
		self.assertEqual(experimentUtils.f_measure(self.set_4, self.set_1), 0.0)
		self.assertEqual(experimentUtils.f_measure(self.set_4, self.set_3), 0.0)
		self.assertTrue(math.isnan(experimentUtils.f_measure(self.set_4, self.set_4)))

	def test_vote(self):
		self.assertEqual(set(experimentUtils.vote([self.set_1, self.set_2, self.set_3], 1)), set(['a', 'b', 'c', 'd', 'e', 'f', 'g']))
		self.assertEqual(set(experimentUtils.vote([self.set_1, self.set_2, self.set_3], 2)), set(['b', 'c', 'e']))
		self.assertEqual(set(experimentUtils.vote([self.set_1, self.set_2, self.set_3], 3)), set([]))


if __name__ == '__main__':
	unittest.main()