from __future__ import division
from context    import ROOT_DIR, dataUtils

import numpy as np

import csv
import os



def getSmells(systemName):
	decorMetricsFile = os.path.join(ROOT_DIR, 'data/metric_files/decor/' + systemName + '.csv')
	
	smells = []
	with open(decorMetricsFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			nmdNad      = float(row['NMD+NAD'])
			nmdNadBound = float(row['nmdNadBound'])
			lcom5       = float(row['LCOM5'])
			lcom5Bound  = float(row['lcom5Bound'])
			cc          = int(row['ControllerClass'])
			nbDataClass = int(row['nbDataClass'])

			if nbDataClass > 0:
				if nmdNad/nmdNadBound > 1:
					smells.append(row['ClassName'])

				elif lcom5/lcom5Bound > 1:
					smells.append(row['ClassName']) 

				elif cc == 1:
					smells.append(row['ClassName'])

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
