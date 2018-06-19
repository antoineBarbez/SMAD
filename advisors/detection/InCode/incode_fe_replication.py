from __future__ import division

import csv
import re
import sys

sys.path.insert(0, '../')
import evaluate

#sys.path.insert(0, '../../../')
#import dataConstruction.entityUtils

''' This file is just used to obtain JDeodorant detection results on the test set'''

'''def normalizeSourceEntity(source_entity):
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

	return methodName + '(' + ', '.join(normalizedParamList) + ')'''

def getClasses(systemName):
	classFile = '../../../data/entities/classes_all/' + systemName + '.csv'

	classes = []
	with open(classFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			classes.append(row['Entity'])

	return classes


def feature_envy(systemName):
	incodeMetricsFile = '../../metrics_files/feature_envy/InCode/' + systemName + '.csv'

	classes = getClasses(systemName)
	
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
			className = row['Class']

			if (i == 0):
				currentMethodName = methodName
				currentClassName = className

			if (currentMethodName != methodName):
				enviedClass = getEnviedClasses(currentClassName, classAttributeDictionnary)
				for klass in enviedClass:
					if (klass in classes):
						smells.append(currentMethodName + ';' + klass)


				classAttributeDictionnary = {}
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])
				currentMethodName = methodName
				currentClassName = className
			else:
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])

			if (i == nbLines):
				currentMethodName = methodName
				currentClassName = className
				classAttributeDictionnary[row['DeclaringClass']] = int(row['NbFields'])
				
				enviedClass = getEnviedClasses(currentClassName, classAttributeDictionnary)
				for klass in enviedClass:
					if (klass in classes):
						smells.append(currentMethodName + ';' + klass)

			i = i + 1


	return list(set(smells))

def getEnviedClasses(className, classAttributeDictionnary):
	enviedClass = []

	FDP = len(classAttributeDictionnary)

	# ATSD: Access To Self Data
	if className in classAttributeDictionnary:
		ATSD = classAttributeDictionnary[className]
		FDP = FDP - 1
	else:
		# To avoid division by zero
		ATSD = 0.5

	for klass in classAttributeDictionnary:
		ATFD = int(classAttributeDictionnary[klass])

		if ((ATFD > 3) & (ATFD/ATSD > 3.0) & (klass != className)):
			enviedClass.append(klass)

	if FDP >= 3:
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
			true.append(row[0] + ';' + row[1])

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

	systems = ['pmd', 'jedit', 'argouml', 'jhotdraw', 'apache-log4j1', 'apache-log4j2', 'mongodb', 'apache-derby', 'junit', 'jgraphx', 'android-frameworks-opt-telephony', 'lucene', 'xerces-2_7_0', 'jspwiki', 'jgroups', 'javacc', 'jena', 'apache-velocity', 'apache-tomcat', 'android-platform-support', 'apache-ant']
	for system in systems:
		smel = feature_envy(system)
		print(system + ": " + str(len(smel)))

	




	