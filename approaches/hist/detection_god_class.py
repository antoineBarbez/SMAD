from context import ROOT_DIR

import utils.detection_utils as detection_utils
import core_metrics as cm

import os

# Returns the set of detected occurrences (class names)
def detect(systemName):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'hist', 'god_class', systemName + '.csv')

	params = detection_utils.get_optimal_hyperparameters(tuning_file)

	core_metrics_map = cm.getGCCoreMetrics(systemName)

	return [className for className, ratio in core_metrics_map.items() if ratio[0]>params['Alpha']]

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('god_class', systemName, detect(systemName))
