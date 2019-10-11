from context import ROOT_DIR

import utils.detection_utils as detection_utils
import core_metrics as cm

import csv
import os

# Returns the set of detected occurrences (class names)
def detect(systemName):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'incode', systemName + '.csv')

	params = detection_utils.get_optimal_hyperparameters(tuning_file)
	return detect_with_params(systemName, params['ATFD'], params['LAA'], params['FDP'])

def detect_with_params(systemName, atfd, laa, fdp):
	core_metrics_map = cm.getFECoreMetrics(systemName)

	smells = []
	for entity in core_metrics_map:
		core_metrics = core_metrics_map[entity]
		ATFD = core_metrics[0]
		LAA  = core_metrics[1]
		FDP  = core_metrics[2]

		if ((ATFD > atfd) & (LAA > laa) & (FDP <= fdp)):
			smells.append(entity)

	return smells

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('feature_envy', systemName, detect(systemName))
