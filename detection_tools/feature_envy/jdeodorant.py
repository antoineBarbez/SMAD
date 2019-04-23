from __future__ import division
from context    import ROOT_DIR, dataUtils, entityUtils

import numpy as np

import os

def getSmells(systemName):
	JDFEFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_output/' + systemName + '.txt')

	methods = dataUtils.getMethods(systemName)
	smells = []
	with open(JDFEFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				source_entity = line.split('\t')[1].replace('::', '.')
				source_entity = source_entity.split(':')[0]
				source_entity = entityUtils.normalizeMethodName(source_entity)
				target_class = line.split('\t')[2]

				if source_entity in methods:
					smells.append(source_entity + ';' + target_class)
			i = i + 1

	return list(set(smells))

def predict(systemName):
	entities = dataUtils.getEntities('feature_envy', systemName)
	smells = getSmells(systemName)

	prediction = []
	for entity in entities:
		if entity in smells:
			prediction.append([1.])
		else:
			prediction.append([0.])

	return np.array(prediction)

