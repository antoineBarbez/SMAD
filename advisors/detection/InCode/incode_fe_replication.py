from __future__ import division

import csv
import re
import sys

sys.path.insert(0, '../')
import evaluate

''' This file is just used to obtain JDeodorant detection results on the test set'''

def normalizeSourceEntity(source_entity):
	m1 = re.match('(.+)\((.*)\)', source_entity)

	methodName = m1.group(1)
	parameters = m1.group(2)
	paramList = parameters.split(', ')

	normalizedParamList = []
	for param in paramList:
		normalizedParam = param.split('.')[-1]
		m2 = re.match('(\w*)\W*', normalizedParam)

		normalizedParamList.append(m2.group(1))

	normalizedParamList.sort()

	return methodName + '(' + ', '.join(normalizedParamList) + ')'

def feature_envy(systemName):
	incodeMetricsFile = '../../metrics_files/feature_envy/InCode/' + systemName + '.csv'
	
	smells = []
	currentMethodName = ''
	classAttributeDictionnary = {}
	i = 0
	with open(incodeMetricsFile, 'rb') as csvfile:
		nbLines = len(csvfile.readlines()) - 2
		csvfile.seek(0)

		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			methodName = row['Class'] + '.' + row['Method']

			if (i == 0):
				currentMethodName = methodName

			if (currentMethodName != methodName):
				enviedClass = getEnviedClasses(currentMethodName, classAttributeDictionnary)
				for klass in enviedClass:
					smells.append(currentMethodName + ';' + klass)


				classAttributeDictionnary = {}
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])
				currentMethodName = methodName
			else:
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])

			if (i == nbLines):
				currentMethodName = methodName
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])
				
				enviedClass = getEnviedClasses(currentMethodName, classAttributeDictionnary)
				for klass in enviedClass:
					smells.append(currentMethodName + ';' + klass)

			i = i + 1

	return list(set(smells))

def getEnviedClasses(methodName, classAttributeDictionnary):
	enviedClass = []

	FDP = len(classAttributeDictionnary)

	className = methodName.split('.')
	className.pop()
	className = '.'.join(className)

	# ATSD: Access To Self Data
	if className in classAttributeDictionnary:
		ATSD = classAttributeDictionnary[className]
		FDP = FDP - 1
	else:
		# To avoid division by zero
		ATSD = 0.5

	for klass in classAttributeDictionnary:
		ATFD = int(classAttributeDictionnary[klass])

		if ((ATFD > 4) & (ATFD/ATSD > 3.0) & (klass != className)):
			enviedClass.append(klass)

	if FDP >= 4:
		enviedClass = []

	return enviedClass

def test(systemName):
	print(systemName)
	trueFile = '../../../data/labels/Feature_envy/test/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			print(row[0])
			true.append(normalizeSourceEntity(row[0]) + ';' + row[1])

	# Get classes detected as God Classes
	detected = feature_envy(systemName)
	print(detected)
 
	pre = evaluate.precision(detected, true)
	rec = evaluate.recall(detected, true)
	f_m = evaluate.f_mesure(detected, true)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))

	return f_m


if __name__ == "__main__":
	'''systems = ['apache-tomcat', 'jedit', 'android-platform-support', 'apache-ant']

	for system in systems:
		test(system)
		print("")'''

	smel = feature_envy('apache-ant')

	print(smel)