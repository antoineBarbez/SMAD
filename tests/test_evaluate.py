from context import evaluate

import math
import unittest

class TestDecorGCCM(unittest.TestCase):
	def setUp(self):
		self.set_1 = ['a','b','c','d', 'e']
		self.set_2 = ['b','e', 'f', 'g']
		self.set_3 = ['c']
		self.set_4 = []

	def tearDown(self):
		del self.set_1
		del self.set_2
		del self.set_3
		del self.set_4


	def test_precision(self):
		self.assertEqual(evaluate.precision(self.set_1, self.set_1), 1.0)
		self.assertEqual(evaluate.precision(self.set_1, self.set_2), 0.4)
		self.assertEqual(evaluate.precision(self.set_1, self.set_3), 0.2)
		self.assertEqual(evaluate.precision(self.set_1, self.set_4), 0.0)
		self.assertEqual(evaluate.precision(self.set_2, self.set_1), 0.5)
		self.assertEqual(evaluate.precision(self.set_2, self.set_2), 1.0)
		self.assertEqual(evaluate.precision(self.set_2, self.set_3), 0.0)
		self.assertEqual(evaluate.precision(self.set_3, self.set_1), 1.0)
		self.assertEqual(evaluate.precision(self.set_3, self.set_4), 0.0)
		self.assertTrue(math.isnan(evaluate.precision(self.set_4, self.set_1)))
		self.assertTrue(math.isnan(evaluate.precision(self.set_4, self.set_3)))
		self.assertTrue(math.isnan(evaluate.precision(self.set_4, self.set_4)))

	def test_recall(self):
		self.assertEqual(evaluate.recall(self.set_1, self.set_1), 1.0)
		self.assertEqual(evaluate.recall(self.set_1, self.set_2), 0.5)
		self.assertEqual(evaluate.recall(self.set_1, self.set_3), 1.0)
		self.assertTrue(math.isnan(evaluate.recall(self.set_1, self.set_4)))
		self.assertEqual(evaluate.recall(self.set_2, self.set_1), 0.4)
		self.assertEqual(evaluate.recall(self.set_2, self.set_2), 1.0)
		self.assertEqual(evaluate.recall(self.set_2, self.set_3), 0.0)
		self.assertEqual(evaluate.recall(self.set_3, self.set_1), 0.2)
		self.assertTrue(math.isnan(evaluate.recall(self.set_3, self.set_4)))
		self.assertEqual(evaluate.recall(self.set_4, self.set_1), 0.0)
		self.assertEqual(evaluate.recall(self.set_4, self.set_3), 0.0)
		self.assertTrue(math.isnan(evaluate.recall(self.set_4, self.set_4)))

	def test_f_measure(self):
		self.assertEqual(evaluate.f_measure(self.set_1, self.set_1), 1.0)
		self.assertEqual(evaluate.f_measure(self.set_1, self.set_2), 0.4444444444444445)
		self.assertEqual(evaluate.f_measure(self.set_1, self.set_3), 0.33333333333333337)
		self.assertTrue(math.isnan(evaluate.f_measure(self.set_1, self.set_4)))
		self.assertEqual(evaluate.f_measure(self.set_2, self.set_1), 0.4444444444444445)
		self.assertEqual(evaluate.f_measure(self.set_2, self.set_2), 1.0)
		self.assertEqual(evaluate.f_measure(self.set_2, self.set_3), 0.0)
		self.assertEqual(evaluate.f_measure(self.set_3, self.set_1), 0.33333333333333337)
		self.assertTrue(math.isnan(evaluate.f_measure(self.set_3, self.set_4)))
		self.assertTrue(math.isnan(evaluate.f_measure(self.set_4, self.set_1)))
		self.assertTrue(math.isnan(evaluate.f_measure(self.set_4, self.set_3)))
		self.assertTrue(math.isnan(evaluate.f_measure(self.set_4, self.set_4)))



if __name__ == '__main__':
	unittest.main()