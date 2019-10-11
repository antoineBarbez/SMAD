import utils.data_utils as data_utils
import utils.detection_utils as detection_utils

import approaches.asci.detection as asci
import approaches.decor.detection as decor
import approaches.hist.detection_god_class as hist_gc
import approaches.jdeodorant.detection_god_class as jdeodorant_gc
import approaches.smad.detection as smad
import approaches.vote.detection as vote

import numpy as np

systems = data_utils.getSystems()

overall_prediction_decor = np.empty(shape=[0, 1])
overall_prediction_hist  = np.empty(shape=[0, 1])
overall_prediction_jd    = np.empty(shape=[0, 1])
overall_prediction_vote  = np.empty(shape=[0, 1])
overall_prediction_asci  = np.empty(shape=[0, 1])
overall_prediction_smad  = np.empty(shape=[0, 1])

overall_labels = np.empty(shape=[0, 1])
for system in systems:
	# Get labels
	labels = detection_utils.getLabels('god_class', system)
	overall_labels = np.concatenate((overall_labels, labels), axis=0)

	# Compute performances for DECOR
	prediction_decor = decor.predict(system)
	overall_prediction_decor = np.concatenate((overall_prediction_decor, prediction_decor), axis=0)

	# Compute performances for HIST
	prediction_hist = hist_gc.predict(system)
	overall_prediction_hist = np.concatenate((overall_prediction_hist, prediction_hist), axis=0)

	# Compute performances for JDeodorant
	prediction_jd = jdeodorant_gc.predict(system)
	overall_prediction_jd = np.concatenate((overall_prediction_jd, prediction_jd), axis=0)

	# Compute performances for Vote
	prediction_vote = vote.predict('god_class', system)
	overall_prediction_vote = np.concatenate((overall_prediction_vote, prediction_vote), axis=0)

	# Compute performances for ASCI
	prediction_asci = asci.predict('god_class', system)
	overall_prediction_asci = np.concatenate((overall_prediction_asci, prediction_asci), axis=0)

	# Compute performances for SMAD
	prediction_smad = smad.predict('god_class', system)
	overall_prediction_smad = np.concatenate((overall_prediction_smad, prediction_smad), axis=0)

	# Print performances for the considered system
	print(system)
	print('           |precision |recall    |mcc')
	print('-------------------------------------------')
	print('DECOR      |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_decor, labels), detection_utils.recall(prediction_decor, labels), detection_utils.mcc(prediction_decor, labels)))
	print('-------------------------------------------')
	print('HIST       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_hist, labels), detection_utils.recall(prediction_hist, labels), detection_utils.mcc(prediction_hist, labels)))
	print('-------------------------------------------')
	print('JDeodorant |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_jd, labels), detection_utils.recall(prediction_jd, labels), detection_utils.mcc(prediction_jd, labels)))
	print('-------------------------------------------')
	print('Vote       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_vote, labels), detection_utils.recall(prediction_vote, labels), detection_utils.mcc(prediction_vote, labels)))
	print('-------------------------------------------')
	print('ASCI       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_asci, labels), detection_utils.recall(prediction_asci, labels), detection_utils.mcc(prediction_asci, labels)))
	print('-------------------------------------------')
	print('SMAD       |{0:.3f}     |{1:.3f}       |{2:.3f}'.format(detection_utils.precision(prediction_smad, labels), detection_utils.recall(prediction_smad, labels), detection_utils.mcc(prediction_smad, labels)))
	print('-------------------------------------------')
	print('\n')

# Print overall performances
print('OVERALL')
print('           |precision |recall    |mcc')
print('-------------------------------------------')
print('DECOR      |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_decor, overall_labels), detection_utils.recall(overall_prediction_decor, overall_labels), detection_utils.mcc(overall_prediction_decor, overall_labels)))
print('-------------------------------------------')
print('HIST       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_hist, overall_labels), detection_utils.recall(overall_prediction_hist, overall_labels), detection_utils.mcc(overall_prediction_hist, overall_labels)))
print('-------------------------------------------')
print('JDeodorant |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_jd, overall_labels), detection_utils.recall(overall_prediction_jd, overall_labels), detection_utils.mcc(overall_prediction_jd, overall_labels)))
print('-------------------------------------------')
print('Vote       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_vote, overall_labels), detection_utils.recall(overall_prediction_vote, overall_labels), detection_utils.mcc(overall_prediction_vote, overall_labels)))
print('-------------------------------------------')
print('ASCI       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_asci, overall_labels), detection_utils.recall(overall_prediction_asci, overall_labels), detection_utils.mcc(overall_prediction_asci, overall_labels)))
print('-------------------------------------------')
print('SMAD       |{0:.3f}     |{1:.3f}     |{2:.3f}'.format(detection_utils.precision(overall_prediction_smad, overall_labels), detection_utils.recall(overall_prediction_smad, overall_labels), detection_utils.mcc(overall_prediction_smad, overall_labels)))
print('-------------------------------------------')
