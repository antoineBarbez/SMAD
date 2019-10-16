from context import ROOT_DIR

import utils.detection_utils as detection_utils
import model      as md
import tensorflow as tf

import os
import smad_utils

# Returns the set of detected occurrences
def detect(antipattern, systemName):
	return detectionUtils.detectFromPredict(antipattern, systemName, predict(antipattern, systemName))

# Returns a vector containing the predictions for each code component of the system
def predict(antipattern, system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'smad', antipattern, system + '.csv')

	params = detection_utils.get_optimal_hyperparameters(tuning_file)
	X = detection_utils.getInstances(antipattern, system)

	# New graph
	tf.reset_default_graph()

	# Create model
	model = md.SMAD(
		shape=params['Dense sizes'], 
		input_size=X.shape[-1])

	return smad_utils.ensemble_prediction(
		model=model,
		save_paths=[smad_utils.get_save_path(antipattern, system, i) for i in range(10)], 
		input_x=X)