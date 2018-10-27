from __future__ import division

import numpy as np

import dataUtils


### EVALUATION ###
def recall(detected, true):	
	truePositive = [entity for entity in detected if entity in true]

	if len(true) == 0:
		return float('nan')

	return len(truePositive) / len(true)

def precision(detected, true):
	truePositive = [entity for entity in detected if entity in true]

	if len(detected) == 0:
		return 0.0

	return len(truePositive) / len(detected)

def f_measure(detected, true, alpha=0.5):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if ((pre == 0) & (rec == 0)):
		return 0.0

	return pre*rec/(alpha*rec + (1-alpha)*pre)


### UTILS ###

# Outputs instances (i.e, class for God Class and method;enviedClass for Feature Envy) 
# detected using a vote over various tools outputs.
# tools_outputs: list containing the lists of instances detected by each tool
# k: mininum number of agreement to detect an instance
def vote(tools_outputs, k):
	assert k <= len(tools_outputs), "k can't be greater than the number of tools"

	# Map instances to the number of tools that have detected this instance
	instanceToNbToolMap = {}
	for detected in tools_outputs:
		for instance in detected:
			if instance in instanceToNbToolMap:
				instanceToNbToolMap[instance] = instanceToNbToolMap[instance] + 1
			else:
				instanceToNbToolMap[instance] = 1

	return [instance for instance in instanceToNbToolMap if instanceToNbToolMap[instance] >= k]
