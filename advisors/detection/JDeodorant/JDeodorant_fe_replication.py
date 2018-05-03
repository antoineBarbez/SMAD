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
	JDFEFile = '../../results/JDeodorant/Feature_envy/' + systemName + '.txt'
	
	smells = []
	with open(JDFEFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				source_entity = line.split('\t')[1].replace('::', '.')
				source_entity = source_entity.split(':')[0]
				source_entity = normalizeSourceEntity(source_entity)
				target_class = line.split('\t')[2]
				smells.append(source_entity + ';' + target_class)
			i = i + 1

	return list(set(smells))


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
	systems = ['apache-tomcat', 'jedit', 'android-platform-support', 'apache-ant']

	for system in systems:
		test(system)
		print("")
