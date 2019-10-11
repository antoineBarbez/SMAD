from context import ROOT_DIR

import approaches.asci.asci_utils as asci_utils
import utils.detection_utils as detection_utils
import numpy as np

import os

# Returns the set of detected occurrences
def detect(antipattern, systemName):
	return detectionUtils.detectFromPredict(antipattern, systemName, predict(antipattern, systemName))

# Returns a vector containing the predictions for each code component of the system
def predict(antipattern, system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'vote', antipattern, test_system + '.csv')
	params = detection_utils.get_optimal_hyperparameters(tuning_file)
	k = params['Policy']
	
	toolsPredictions = asci_utils.get_tools_predictions(antipattern, system)

	return (np.sum(toolsPredictions, axis=0) >= k).astype(float)