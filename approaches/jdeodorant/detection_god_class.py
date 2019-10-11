import utils.detection_utils as detection_utils
import core_metrics as cm

import os

# Returns the set of detected occurrences (class names)
def detect(systemName):
	core_metrics_map = cm.getGCCoreMetrics(systemName)
	return [key for key in core_metrics_map]

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('god_class', systemName, detect(systemName))