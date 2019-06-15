from context import ROOT_DIR, dataUtils, entityUtils

import os

def detect(systemName):
	JDFEFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'jdeodorant', 'feature_envy_output', systemName + '.txt')

	methods = dataUtils.getMethods(systemName)
	smells = []
	with open(JDFEFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				source_entity = line.split('\t')[1].replace('::', '.')
				source_entity = source_entity.split(':')[0]
				source_entity = entityUtils.normalizeMethodName(source_entity)
				target_class = line.split('\t')[2]

				if source_entity in methods:
					smells.append(source_entity + ';' + target_class)
			i = i + 1

	return list(set(smells))
