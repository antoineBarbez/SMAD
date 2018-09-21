from __future__ import division


def recall(detected, true):	
	truePositive = [entity for entity in detected if entity in true]

	if len(true) == 0:
		return float('nan')

	return len(truePositive) / len(true)

def precision(detected, true):
	truePositive = [entity for entity in detected if entity in true]

	if len(detected) == 0:
		return float('nan')

	return len(truePositive) / len(detected)

def f_measure(detected, true, alpha=0.5):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if ((pre == 0) & (rec == 0)):
		return 0.0

	return pre*rec/(alpha*rec + (1-alpha)*pre)