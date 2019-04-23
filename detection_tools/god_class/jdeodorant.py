from context import ROOT_DIR, dataUtils

import numpy as np

import os


def getSmells(systemName):
	JDBlobFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/god_class_output/' + systemName + '.txt')
	
	with open(JDBlobFile, 'r') as file:
		return list(set([line.split()[0] for line in file]))

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
