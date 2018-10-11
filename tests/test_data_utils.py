from context import dataUtils, entityUtils

import unittest


class TestDataUtils(unittest.TestCase):
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

	def tearDown(self):
		del self.systems

	def test_getCandidateFeatureEnvy(self):
		for system in self.systems:
			methods = dataUtils.getMethods(system)
			classes = dataUtils.getAllClasses(system)
			candidates = dataUtils.getCandidateFeatureEnvy(system)

			for entity in candidates:
				method = entity.split(';')[0]
				embeddingClass = entityUtils.getEmbeddingClass(method)
				enviedClass = entity.split(';')[1]

				assert method in methods
				assert embeddingClass in classes
				assert enviedClass in classes
				assert embeddingClass != enviedClass
		

	def test_getFEHistMetrics(self):
		feHistMetrics = dataUtils.getFEHistMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.DataConnectionTracker.doRecovery()'
		enviedClass = 'com.android.internal.telephony.ServiceStateTracker'

		self.assertAlmostEqual(feHistMetrics[method + ';' + enviedClass][0], 0.0, 5)


		feHistMetrics = dataUtils.getFEHistMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.IccSmsInterfaceManager.sendData(byte, int, pendingintent, pendingintent, string, string)'
		enviedClass = 'com.android.internal.telephony.SMSDispatcher'

		self.assertAlmostEqual(feHistMetrics[method + ';' + enviedClass][0], 1.0, 5)


		feHistMetrics = dataUtils.getFEHistMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.IccPhoneBookInterfaceManager.updateEfForIccType(int)'
		enviedClass = 'com.android.internal.telephony.PhoneBase'

		self.assertAlmostEqual(feHistMetrics[method + ';' + enviedClass][0], 4.0, 5)


	def test_getFEInCodeMetrics(self):
		feInCodeMetrics = dataUtils.getFEInCodeMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.DataConnectionTracker.doRecovery()'
		enviedClass = 'com.android.internal.telephony.ServiceStateTracker'
		values = [0.0, 0.0, 0.0]
		for i in range(3): 
			self.assertAlmostEqual(feInCodeMetrics[method + ';' + enviedClass][i], values[i], 5)


		feInCodeMetrics = dataUtils.getFEInCodeMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.gsm.GSMPhone.getMsisdn()'
		enviedClass = 'com.android.internal.telephony.uicc.IccRecords'
		values = [0.333333, 0.333333, 0.333333]
		for i in range(3): 
			self.assertAlmostEqual(feInCodeMetrics[method + ';' + enviedClass][i], values[i], 5)

		feInCodeMetrics = dataUtils.getFEInCodeMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.IccPhoneBookInterfaceManager.updateEfForIccType(int)'
		enviedClass = 'com.android.internal.telephony.PhoneBase'
		values = [0.333333, 0.333333, 0.666666]
		for i in range(3): 
			self.assertAlmostEqual(feInCodeMetrics[method + ';' + enviedClass][i], values[i], 5)


	def test_someValues_getFEJDeodorantMetrics(self):
		feJDMetrics = dataUtils.getFEJDeodorantMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.DataConnectionTracker.doRecovery()'
		enviedClass = 'com.android.internal.telephony.ServiceStateTracker'
		values = [0.125, 1.0317460317460316, 0.0]
		for i in range(3): 
			self.assertAlmostEqual(feJDMetrics[method + ';' + enviedClass][i], values[i], 5)


		feJDMetrics = dataUtils.getFEJDeodorantMetrics('android-frameworks-opt-telephony')
		method = 'com.android.internal.telephony.gsm.GSMPhone.getMsisdn()'
		enviedClass = 'com.android.internal.telephony.uicc.IccRecords'
		values = [2.0, 0.9795918367346939, 0.0]
		for i in range(3): 
			self.assertAlmostEqual(feJDMetrics[method + ';' + enviedClass][i], values[i], 5)

		feJDMetrics = dataUtils.getFEJDeodorantMetrics('android-frameworks-opt-telephony')
		method = 'android.telephony.CellBroadcastMessage.getCmasMessageClass()'
		enviedClass = 'android.telephony.SmsCbMessage'
		values = [2.0, 0.9375, 1.0]
		for i in range(3): 
			self.assertAlmostEqual(feJDMetrics[method + ';' + enviedClass][i], values[i], 5)



if __name__ == '__main__':
	unittest.main()