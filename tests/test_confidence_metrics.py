from context import cm, dataUtils

import unittest

class TestDecorGCCM(unittest.TestCase):
	def setUp(self):
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

		self.classes = map(reader.getClasses, self.systems)

	def tearDown(self):
		del self.systems
		del self.classes


	def test_compute_decor_gccm(self):
		self.assertEqual(cm.computeDecorGCCM(0, 1, 0, 1, 0, 0), 0)
		self.assertEqual(cm.computeDecorGCCM(7.5, 3.2, 10, 2.5, 0, 3), 11.703125)
		self.assertEqual(cm.computeDecorGCCM('223.1', '12.88872', '1', '21', '1', '2'), 16.30952380952381)

	def test_get_decor_gccm(self):
		for i, system in enumerate(self.systems):
			confidence_metrics = cm.getDecorGCCM(system)
			self.assertEqual(len(confidence_metrics), len(self.classes[i]))

	def test_get_jdeodorant_gccm(self):
		for i, system in enumerate(self.systems):
			confidence_metrics = cm.getJDeodorantGCCM(system)
			self.assertEqual(len(confidence_metrics), len(self.classes[i]))

	def test_get_hist_gccm(self):
		for i, system in enumerate(self.systems):
			confidence_metrics = cm.getHistGCCM(system)
			self.assertEqual(len(confidence_metrics), len(self.classes[i]))



if __name__ == '__main__':
	unittest.main()