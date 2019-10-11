from context import ROOT_DIR

import utils.detection_utils as detection_utils
import core_metrics as cm

import os

# Returns the set of detected occurrences
def detect(systemName):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'hist', 'feature_envy', systemName + '.csv')

	params = detection_utils.get_optimal_hyperparameters(tuning_file)

	core_metrics_map = cm.getFECoreMetrics(systemName)

	return [entityName for entityName, ratio in core_metrics_map.items() if ratio[0]>params['Alpha']]

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('feature_envy', systemName, detect(systemName))
