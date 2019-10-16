from context import ROOT_DIR

import utils.data_utils as data_utils
import utils.detection_utils as detection_utils
import utils.java_utils as java_utils

import os

# Returns the set of detected occurrences
def detect(systemName):
	JDFEFile = os.path.join(ROOT_DIR, 'approaches', 'jdeodorant', 'metric_files', 'feature_envy_output', systemName + '.txt')

	methods = data_utils.getMethods(systemName)
	smells = []
	with open(JDFEFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				source_entity = line.split('\t')[1].replace('::', '.')
				source_entity = source_entity.split(':')[0]
				source_entity = java_utils.normalizeMethodName(source_entity)
				target_class = line.split('\t')[2]

				if source_entity in methods:
					smells.append(source_entity + ';' + target_class)
			i = i + 1

	return list(set(smells))

# Returns a vector containing the predictions for each code component of the system
def predict(systemName):
	return detection_utils.predictFromDetect('feature_envy', systemName, detect(systemName))