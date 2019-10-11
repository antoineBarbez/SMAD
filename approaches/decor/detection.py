import utils.detection_utils as detection_utils

import core_metrics as cm

# Returns the set of detected occurrences (class names)
def detect(systemName):
	core_metrics_map = cm.getGCCoreMetrics(systemName)

	smells = []
	for className in core_metrics_map:
		core_metrics = core_metrics_map[className]
		
		nmdnad      = core_metrics[0]
		lcom5       = core_metrics[1]
		cc          = core_metrics[2]
		nbDataClass = core_metrics[3]

		if nbDataClass > 0:
			if nmdnad > 1:
				smells.append(className)

			elif lcom5 > 1:
				smells.append(className) 

			elif cc == 1:
				smells.append(className)

	return smells

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('god_class', systemName, detect(systemName))