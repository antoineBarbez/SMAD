from context import nnUtils, decor, incode, hist_gc, hist_fe, jdeodorant_gc, jdeodorant_fe
from sklearn import tree

import numpy as np

import pickle

# Returns a list containing the predictions of each approach/tool.
def getToolsPredictions(antipattern, system):
	assert antipattern in ['god_class', 'feature_envy']
	if antipattern == 'god_class':
		toolsOutputs = [decor.detect(system), hist_gc.detect(system), jdeodorant_gc.detect(system)]
	else:
		toolsOutputs = [incode.detect(system), hist_fe.detect(system), jdeodorant_fe.detect(system)]

	return map(lambda x: nnUtils.predictFromDetect(antipattern, system, x), toolsOutputs)

def predict(antipattern, system):
	toolsPredictions = getToolsPredictions(antipattern, system)
	X = nnUtils.getInstances(antipattern, system, True)

	# Compute ensemble prediction over 10 pre-trained classifiers
	predictions = np.zeros((10, X.shape[0], 1))
	for i in range(10):
		with open(nnUtils.get_save_path('asci', antipattern, system, i), 'r') as file:
			clf = pickle.load(file)
			predictedToolIndexes = clf.predict(X)
			for j, toolIndex in enumerate(predictedToolIndexes): 
				predictions[i, j, 0] = toolsPredictions[toolIndex][j]
  	
	return np.mean(predictions, axis=0)