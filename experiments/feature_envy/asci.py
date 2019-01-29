from context import experimentUtils, dataUtils, nnUtils, hist, incode, jdeodorant
from sklearn import tree

import numpy as np


training_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']

def getToolIndexes(system):
	entities = dataUtils.getCandidateFeatureEnvy(system)
	antipatterns = dataUtils.getAntipatterns(system, 'feature_envy')
	detected = [hist.getSmells(system), jdeodorant.getSmells(system), incode.getSmells(system)]

	toolIndexes = [2 for e in entities]
	for i, e in enumerate(entities):
		if e in antipatterns:
			for toolIdx, detected_tool in enumerate(detected):
				if e in detected_tool:
					toolIndexes[i] = toolIdx

		else:
			for toolIdx, detected_tool in enumerate(detected):
				if e not in detected_tool:
					toolIndexes[i] = toolIdx

	return toolIndexes

X = []
Y = []
for system in training_systems:
	X += nnUtils.getInstances(system, 'feature_envy', False).tolist()
	Y += getToolIndexes(system)

clf = tree.DecisionTreeClassifier()
clf = clf.fit(X, Y)

def getSmells(system):
	instances = nnUtils.getInstances(system, 'feature_envy', False)
	predictedToolIndexes = clf.predict(instances)

	entities = dataUtils.getCandidateFeatureEnvy(system)
	detected = [hist.getSmells(system), jdeodorant.getSmells(system), incode.getSmells(system)]

	smells = []
	for i, e in enumerate(entities):
		if e in detected[predictedToolIndexes[i]]:
			smells.append(e)

	return smells