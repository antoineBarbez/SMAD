from __future__ import division


def recall(detected, true):
	truePos = 0
	for className in detected:
		if className in true:
			truePos += 1 

	if len(true) == 0:
		return 0

	return truePos / len(true)

def precision(detected, true):
	truePos = 0
	for className in detected:
		if className in true:
			truePos += 1

	if len(detected) == 0:
		return 0 

	return truePos / len(detected)

def f_mesure(detected, true, alpha=0.5):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if (pre + rec) ==0:
		return 0

	return pre*rec/(alpha*rec + (1-alpha)*pre)