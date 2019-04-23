from __future__ import division
from context    import dataUtils

import numpy as np


def getSmells(systemName, alpha=8.0):
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

def predict(systemName):
	entities = dataUtils.getEntities('god_class', systemName)
	smells = getSmells(systemName)

	prediction = []
	for entity in entities:
		if entity in smells:
			prediction.append([1.])
		else:
			prediction.append([0.])

	return np.array(prediction)

