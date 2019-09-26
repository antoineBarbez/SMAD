from context import ROOT_DIR, nnUtils, decor, incode, hist_gc, hist_fe, jdeodorant_gc, jdeodorant_fe

import numpy as np

import csv
import os

def getOptimalPolicy(antipattern, test_system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'vote', antipattern, test_system + '.csv')

	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['MCC'] != 'nan':
				return int(row['Policy'])

def getToolsPredictions(antipattern, system):
	if antipattern == 'god_class':
		toolsDetections = [decor.detect(system), hist_gc.detect(system), jdeodorant_gc.detect(system)]
	else:
		toolsDetections = [incode.detect(system), hist_fe.detect(system), jdeodorant_fe.detect(system)]

	toolsPredictions =  np.array(map(lambda x: nnUtils.predictFromDetect(antipattern, system, x), toolsDetections))

	return np.array(map(lambda x: np.array(x).flatten(), toolsPredictions))

def predict(antipattern, system):
	k = getOptimalPolicy(antipattern, system)
	toolsPredictions = getToolsPredictions(antipattern, system)

	return vote(toolsPredictions, k)

def vote(predictions, k):
	assert k <= len(predictions), "k can't be greater than the number of tools"

	flat_vote_prediction = (np.sum(predictions, axis=0) >= k).astype(float)

	return np.reshape(flat_vote_prediction, (-1, 1))