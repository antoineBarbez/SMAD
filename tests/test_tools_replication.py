from context import hist_fe, incode_fe, jdeodorant_fe

import unittest

class ToolsReplicationTest(unittest.TestCase):

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

		self.hist_params = 2.0

		self.incode_params = (3.0, 3.0, 3.0)

	def tearDown(self):
		del self.systems
		del self.hist_params
		del self.incode_params


	def test_hist_fe(self):
		smells = []
		for system in self.systems:
			smells += hist_fe.getSmells(system, self.hist_params)

		self.assertEqual(len(smells), 346)

	def test_incode_fe(self):
		smells = []
		for system in self.systems:
			smells += incode_fe.getSmells(system, *self.incode_params)

		self.assertEqual(len(smells), 204)

	def test_jdeodorant_fe(self):
		smells = []
		for system in self.systems:
			smells += jdeodorant_fe.getSmells(system)
		
		self.assertEqual(len(smells), 199)


if __name__ == "__main__":
	unittest.main()