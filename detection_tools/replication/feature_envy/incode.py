from __future__ import division
from context    import ROOT_DIR, reader, entityUtils

import csv


def getSmells(systemName, atfd, laa, fdp):
	incodeMetricsFile = ROOT_DIR + '/detection_tools/metrics_files/feature_envy/InCode/' + systemName + '.csv'

	classes = reader.getAllClasses(systemName)
	methods = reader.getMethods(systemName)
	
	smells = []
	currentMethodName = ''
	classAttributeMap = {}
	i = 0
	with open(incodeMetricsFile, 'rb') as csvfile:
		nbLines = len(csvfile.readlines()) - 2
		csvfile.seek(0)

		rdr = csv.DictReader(csvfile, delimiter=';')
		for row in rdr:
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

'''
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

	return f_m'''


if __name__ == "__main__":
	systems = ['android-frameworks-opt-telephony', 'android-platform-support', 'apache-ant', 'apache-tomcat', 'lucene', 'argouml', 'jedit', 'xerces-2_7_0']

	for system in systems:
		nbClass = getClasses(system)
		print(system + ': ' + str(len(nbClass)))


	'''systems = ['apache-tomcat', 'jedit', 'android-platform-support', 'apache-ant']

	for system in systems:
		test(system)
		print("")'''

	'''systems = ['pmd', 'jedit', 'argouml', 'jhotdraw', 'apache-log4j1', 'apache-log4j2', 'mongodb', 'apache-derby', 'junit', 'jgraphx', 'android-frameworks-opt-telephony', 'lucene', 'xerces-2_7_0', 'jspwiki', 'jgroups', 'javacc', 'jena', 'apache-velocity', 'apache-tomcat', 'android-platform-support', 'apache-ant']
	for system in systems:
		smel = feature_envy(system)
		print(system + ": " + str(len(smel)))'''

	




	