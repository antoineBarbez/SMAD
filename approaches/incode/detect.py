from __future__ import division
from context    import ROOT_DIR, dataUtils, entityUtils, nnUtils

import csv
import os

def detect(systemName):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'incode', systemName + '.csv')

	params = nnUtils.get_optimal_hyperparameters(tuning_file)
	return detect_with_params(systemName, params['ATFD'], params['LAA'], params['FDP'])

def detect_with_params(systemName, atfd, laa, fdp):
	incodeMetricsFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'incode', systemName + '.csv')

	classes = dataUtils.getAllClasses(systemName)
	methods = dataUtils.getMethods(systemName)
	
	smells = []
	currentMethodName = ''
	classAttributeMap = {}
	i = 0
	with open(incodeMetricsFile, 'rb') as csvfile:
		nbLines = len(csvfile.readlines()) - 2
		csvfile.seek(0)

		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			className = row['Class']
			methodName = className + '.' + row['Method']

			if (i == 0):
				currentMethodName = methodName
				currentClassName = className

			if (currentMethodName != methodName):
				enviedClass = getEnviedClasses(currentClassName, classAttributeMap, atfd, laa, fdp)
				normMethodName = entityUtils.normalizeMethodName(currentMethodName)
				for klass in enviedClass:
					if (klass in classes) & (normMethodName in methods):
						smells.append(normMethodName + ';' + klass)


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
				
				enviedClass = getEnviedClasses(currentClassName, classAttributeMap, atfd, laa, fdp)
				normMethodName = entityUtils.normalizeMethodName(currentMethodName)
				for klass in enviedClass:
					if (klass in classes) & (normMethodName in methods):
						smells.append(normMethodName + ';' + klass)

			i = i + 1


	return list(set(smells))

def getEnviedClasses(className, classAttributeMap, atfd, laa, fdp):
	enviedClass = []

	FDP = len(classAttributeMap)

	# ATSD: Access To Self Data
	if className in classAttributeMap:
		ATSD = classAttributeMap[className]
		FDP = FDP - 1
	else:
		# To avoid division by zero
		ATSD = 0.5

	for klass in classAttributeMap:
		ATFD = int(classAttributeMap[klass])

		if ((ATFD > atfd) & (ATFD/ATSD > laa) & (klass != className)):
			enviedClass.append(klass)

	if FDP > fdp:
		enviedClass = []

	return enviedClass
