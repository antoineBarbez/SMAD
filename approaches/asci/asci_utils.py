from context import ROOT_DIR

import utils.detection_utils as detection_utils

import approaches.decor.detection as decor
import approaches.hist.detection_god_class as hist_gc
import approaches.hist.detection_feature_envy as hist_fe
import approaches.jdeodorant.detection_god_class as jdeodorant_gc
import approaches.jdeodorant.detection_feature_envy as jdeodorant_fe
import approaches.incode.detection as incode

import numpy as np

import os

def get_asci_labels(tools_predictions_list, labels_list):
	'''
	Returns ASCI labels:
		Assign to each instance, the index of the tool that best predicted its label.
		In case of conflict, assign the index of the tool that performed the best on overall.

	args:
		tools_predictions_list: a list containing the tools predictions for a set of systems
		labels_list: a list containing the labels for this same set of systems
	'''

	tools_sorted_indexes = get_tools_sorted_indexes(tools_predictions_list, labels_list)

	asci_labels = []
	for i, tools_predictions in enumerate(tools_predictions_list):
		labels = labels_list[i]
		for j, label in enumerate(labels):
			asci_label = tools_sorted_indexes[-1]
			for tool_index in tools_sorted_indexes:
				if tools_predictions[tool_index, j] == label:
					asci_label = tool_index
			asci_labels.append(asci_label)

	return np.reshape(np.array(asci_labels), (-1, 1))

def get_tools_sorted_indexes(tools_predictions_list, labels_list):
	'''
	Returns the indexes of the tools, sorted according to their performances
		example: 
			if tool 0 is better than tool 1 which is better that tool 2
			then return [2, 1, 0]

	args:
		tools_predictions_list: a list containing the tools predictions for a set of systems
		labels_list: a list containing the labels for this same set of systems
	'''
	assert len(tools_predictions_list) == len(labels_list)

	# Get overall tools' predictions and labels
	overall_labels = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=0), labels_list)
	overall_tools_predictions = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=1), tools_predictions_list)

	# Compute overall preformances for each tool
	overall_tools_performances = [detection_utils.mcc(pred, overall_labels) for pred in overall_tools_predictions]

	return np.argsort(np.array(overall_tools_performances))

def get_tools_predictions(antipattern, system):
	'''
	Returns a list containing the predictions of each tool
	'''
	if antipattern == 'god_class':
		return np.array([decor.predict(system), hist_gc.predict(system), jdeodorant_gc.predict(system)])
	else:
		return np.array([incode.predict(system), hist_fe.predict(system), jdeodorant_fe.predict(system)])

def get_save_path(antipattern, test_system, model_number):
	directory = os.path.join(ROOT_DIR, 'approaches', 'asci', 'trained_models', antipattern, test_system)
	if not os.path.exists(directory):
			os.makedirs(directory)
	return os.path.join(directory, 'model_' + str(model_number))
