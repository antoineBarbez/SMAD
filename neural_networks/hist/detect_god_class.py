from __future__ import division
from context    import ROOT_DIR, dataUtils, nnUtils

import numpy as np

import os

def detect(systemName):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'hist', 'god_class', systemName + '.csv')

	params = nnUtils.get_optimal_hyperparameters(tuning_file)
	return detect_with_params(systemName, params['Alpha'])


def detect_with_params(systemName, alpha):
	# Get and prepare all data needed (classes, history)
	classes = dataUtils.getClasses(systemName)
	classToIndexMap = {klass: i for i, klass in enumerate(classes)}
    
	history = dataUtils.getHistory(systemName, "C")
	
	# Compute for each class, the number of commit involving at least another class,
	# and the number of occurences in this set of commit.
	nbCommit   = np.zeros(len(classes))
	occurences = np.zeros(len(classes))
	for commit in history:
		nbCommit = nbCommit + 1

		if len(commit) > 1:
			for className in commit:
				if className in classes:
					idx = classToIndexMap[className]
					occurences[idx] = occurences[idx] + 1

		else:
			className = commit[0]
			if className in classes:
				idx = classToIndexMap[className]
				nbCommit[idx] = nbCommit[idx] - 1


	# Return all the classes 'involved in more than alpha% of commits involving at least another class'
	smells = []
	for i, nbOcc in enumerate(occurences):
		threshold = nbCommit[i]*alpha/100
		if nbOcc > threshold:
			smells.append(classes[i])


	return smells
