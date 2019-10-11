from sklearn import tree

import utils.detection_utils as detection_utils
import numpy as np

import asci_utils
import pickle

# Returns the set of detected occurrences
def detect(antipattern, systemName):
	return detection_utils.detectFromPredict(antipattern, systemName, predict(antipattern, systemName))

# Returns a vector containing the predictions for each code component of the system
def predict(antipattern, systemName):
	toolsPredictions = asci_utils.get_tools_predictions(antipattern, systemName)
	instances = detection_utils.getInstances(antipattern, systemName)

	# Compute ensemble prediction over 10 pre-trained classifiers
	predictions = np.zeros((10, instances.shape[0], 1))
	for i in range(10):
		with open(asci_utils.get_save_path(antipattern, systemName, i), 'r') as model:
			clf = pickle.load(model)
			predictedToolIndexes = clf.predict(instances)
			for j, toolIndex in enumerate(predictedToolIndexes): 
				predictions[i, j] = toolsPredictions[toolIndex, j]
  	
	return np.mean(predictions, axis=0)