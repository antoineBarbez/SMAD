from __future__ import division
from context    import ROOT_DIR, dataUtils, entityUtils


def getSmells(systemName):
	JDFEFile = ROOT_DIR + '/detection_tools/metrics_files/feature_envy/jdeodorant/' + systemName + '.txt'

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

