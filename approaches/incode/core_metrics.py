from context import ROOT_DIR

import utils.data_utils as data_utils
import utils.entity_utils as entity_utils

import csv
import os


def getFECoreMetrics(systemName):
	incodeMetricsFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'incode', systemName + '.csv')

	dictionnary = {e:[0., 0., 0.] for e in data_utils.getEntities('feature_envy', systemName)}

	classAttributeMap = {}
	with open(incodeMetricsFile, 'rb') as csvfile:
		nbLines = len(csvfile.readlines()) - 2
		csvfile.seek(0)
		i = 0

		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			className = row['Class']
			methodName = className + '.' + row['Method']

			if (i == 0):
				currentMethodName = methodName
				currentClassName = className

			if (currentMethodName != methodName):
				classToMetricMap = getClassToMetricMap(currentClassName, classAttributeMap)
				normMethodName = entity_utils.normalizeMethodName(currentMethodName)
				for klass in classToMetricMap:
					entityName = normMethodName + ';' + klass
					if entityName in dictionnary:
						dictionnary[entityName] = classToMetricMap[klass]

				classAttributeMap = {}
				classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])
				currentMethodName = methodName
				currentClassName = className
			else:
				classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])

			if (i == nbLines):
				currentMethodName = methodName
				currentClassName = className
				classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])

				classToMetricMap = getClassToMetricMap(currentClassName, classAttributeMap)
				normMethodName = entity_utils.normalizeMethodName(currentMethodName)
				for klass in classToMetricMap:
					entityName = normMethodName + ';' + klass
					if entityName in dictionnary:
						dictionnary[entityName] = classToMetricMap[klass]

			i += 1

	return dictionnary


def getClassToMetricMap(className, classAttributeMap):
	classToMetricMap = {}

	# FDP: Foreign Data Providers
	FDP = float(len(classAttributeMap))

	# ATSD: Access To Self Data
	if className in classAttributeMap:
		ATSD = float(classAttributeMap[className])
		FDP = FDP - 1
	else:
		# To avoid division by zero
		ATSD = 0.5

	for klass in classAttributeMap:
		if klass != className:
			#ATFD: Access To Foreign Data
			ATFD = float(classAttributeMap[klass])

			#LAA: Locality of Attribute Access
			LAA  = ATFD/ATSD

			classToMetricMap[klass] = [ATFD, LAA, FDP]

	return classToMetricMap