from context import nnUtils, decor_gc, incode_fe, hist_gc, hist_fe, jdeodorant_gc, jdeodorant_fe
from sklearn import tree

import numpy as np

import pickle

# Returns a list containing the predictions of each approach/tool.
def getToolsPredictions(antipattern, system):
	assert antipattern in ['god_class', 'feature_envy']
	if antipattern == 'god_class':
		return [decor_gc.predict(system), hist_gc.predict(system), jdeodorant_gc.predict(system)]
	else:
		return [incode_fe.predict(system), hist_fe.predict(system), jdeodorant_fe.predict(system)]

def predict(antipattern, system):
	toolsPredictions = getToolsPredictions(antipattern, system)
	X = nnUtils.getInstances(antipattern, system)

	# Ensemble Prediction
	predictions = np.zeros((10, X.shape[0], 1))
	for i in range(10):
		with open(nnUtils.get_save_path(i), 'r') as file:
			clf = pickle.load(file)
			predictedToolIndexes = clf.predict(X)
			for j, toolIndex in enumerate(predictedToolIndexes): 
				predictions[i, j, 0] = toolsPredictions[toolIndex][j]
  	
	return np.mean(predictions, axis=0)