from context import nnUtils, decor, hist_gc, jdeodorant_gc, vote, asci, smad

import numpy as np

systems = [
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant',
	'lucene',
	'apache-tomcat',
	'argouml',
	'jedit',
	'xerces-2_7_0'
]

overall_prediction_decor = np.empty(shape=[0, 1])
overall_prediction_hist = np.empty(shape=[0, 1])
overall_prediction_jd = np.empty(shape=[0, 1])
overall_prediction_vote = np.empty(shape=[0, 1])
#overall_prediction_asci = np.empty(shape=[0, 1])
overall_prediction_smad = np.empty(shape=[0, 1])

overall_labels = np.empty(shape=[0, 1])
for system in systems:
	# Get occurrences manually detected on the considered system
	labels = nnUtils.getLabels('god_class', system)
	overall_labels = np.concatenate((overall_labels, labels), axis=0)

	# Compute performances for DECOR
	prediction_decor = nnUtils.predictFromDetect('god_class', system, decor.detect(system))
	overall_prediction_decor = np.concatenate((overall_prediction_decor, prediction_decor), axis=0)

	# Compute performances for HIST
	prediction_hist = nnUtils.predictFromDetect('god_class', system, hist_gc.detect(system))
	overall_prediction_hist = np.concatenate((overall_prediction_hist, prediction_hist), axis=0)

	# Compute performances for JDeodorant
	prediction_jd = nnUtils.predictFromDetect('god_class', system, jdeodorant_gc.detect(system))
	overall_prediction_jd = np.concatenate((overall_prediction_jd, prediction_jd), axis=0)

	# Compute performances for Vote
	prediction_vote = vote.predict('god_class', system)
	overall_prediction_vote = np.concatenate((overall_prediction_vote, prediction_vote), axis=0)

	# Compute performances for ASCI
	#prediction_asci = asci.predict('god_class', system)
	#overall_prediction_asci = np.concatenate((overall_prediction_asci, prediction_asci), axis=0)

	# Compute performances for SMAD
	prediction_smad = smad.predict('god_class', system)
	overall_prediction_smad = np.concatenate((overall_prediction_smad, prediction_smad), axis=0)

	# Print performances for the considered system
	print(system)
	print('           |precision |recall    |mcc')
	print('-------------------------------------------')
	print('DECOR      |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_decor, labels), nnUtils.recall(prediction_decor, labels), nnUtils.mcc(prediction_decor, labels)))
	print('-------------------------------------------')
	print('HIST       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_hist, labels), nnUtils.recall(prediction_hist, labels), nnUtils.mcc(prediction_hist, labels)))
	print('-------------------------------------------')
	print('JDeodorant |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_jd, labels), nnUtils.recall(prediction_jd, labels), nnUtils.mcc(prediction_jd, labels)))
	print('-------------------------------------------')
	print('Vote       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_vote, labels), nnUtils.recall(prediction_vote, labels), nnUtils.mcc(prediction_vote, labels)))
	print('-------------------------------------------')
	#print('ASCI       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_asci, labels), nnUtils.recall(prediction_asci, labels), nnUtils.mcc(prediction_asci, labels)))
	#print('-------------------------------------------')
	print('SMAD       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(nnUtils.precision(prediction_smad, labels), nnUtils.recall(prediction_smad, labels), nnUtils.mcc(prediction_smad, labels)))
	print('-------------------------------------------')

	print('\n')

# Print overall performances
print('OVERALL')
print('           |precision |recall    |mcc')
print('-------------------------------------------')
print('DECOR      |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_decor, overall_labels), nnUtils.recall(overall_prediction_decor, overall_labels), nnUtils.mcc(overall_prediction_decor, overall_labels)))
print('-------------------------------------------')
print('HIST       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_hist, overall_labels), nnUtils.recall(overall_prediction_hist, overall_labels), nnUtils.mcc(overall_prediction_hist, overall_labels)))
print('-------------------------------------------')
print('JDeodorant |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_jd, overall_labels), nnUtils.recall(overall_prediction_jd, overall_labels), nnUtils.mcc(overall_prediction_jd, overall_labels)))
print('-------------------------------------------')
print('Vote       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_vote, overall_labels), nnUtils.recall(overall_prediction_vote, overall_labels), nnUtils.mcc(overall_prediction_vote, overall_labels)))
print('-------------------------------------------')
#print('ASCI       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_asci, overall_labels), nnUtils.recall(overall_prediction_asci, overall_labels), nnUtils.mcc(overall_prediction_asci, overall_labels)))
#print('-------------------------------------------')
print('SMAD       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(nnUtils.precision(overall_prediction_smad, overall_labels), nnUtils.recall(overall_prediction_smad, overall_labels), nnUtils.mcc(overall_prediction_smad, overall_labels)))
print('-------------------------------------------')
