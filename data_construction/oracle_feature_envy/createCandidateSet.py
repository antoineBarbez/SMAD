from context import ROOT_DIR, entityUtils, hist, incode, jdeodorant

import numpy as np

import csv
import os
import random
import subprocess

'''This script has been used to generate the files in ./candidate_set.
These files have then been used to create some google forms that have been filled 
by several peoples to create our oracle'''


###  PARAMETERS ###

systems = [
		{
		'name'         : 'android-frameworks-opt-telephony',
		'hist_params'  : 1.3,
		'incode_params': (3.0, 4.0, 2.0)
		},
		{
		'name'         : 'android-platform-support',
		'hist_params'  : 1.0,
		'incode_params': (2.0, 2.5, 4.0)
		},
		{
		'name'         : 'apache-ant',
		'hist_params'  : 2.5,
		'incode_params': (3.0, 3.0, 3.0)
		},
		{
		'name'         : 'apache-tomcat',
		'hist_params'  : 2.0,
		'incode_params': (3.0, 3.0, 3.0)
		},
		{
		'name'         : 'lucene',
		'hist_params'  : 1.3,
		'incode_params': (2.0, 2.0, 3.0)
		},
		{
		'name'         : 'argouml',
		'hist_params'  : 2.5,
		'incode_params': (2.0, 3.0, 3.0)
		},
		{
		'name'         : 'jedit',
		'hist_params'  : 2.0,
		'incode_params': (3.0, 3.0, 3.0)
		},
		{
		'name'         : 'xerces-2_7_0',
		'hist_params'  : 2.0,
		'incode_params': (4.0, 3.0, 3.0)
		}
	]


# Returns for a given system, a map as {embeddingClassName:{methodName:enviedClassName}}
# containing all the feature envy instances detected by the tools
def getSmells(system):
	#Get smells
	smells = []
	smells += jdeodorant.detect(system['name'])
	smells += hist.detect_with_params(system['name'], system['hist_params'])
	smells += incode.detect_with_params(system['name'], *system['incode_params'])

	#Shuffle and remove duplicates
	random.shuffle(smells)
	smells = list(set(smells))


	#Create MAP
	MAP = {}
	methodToNameMap = getMethodToNameMap(system['name'])
	for smell in smells:
		methodFullName = smell.split(';')[0]
		embeddingClass = getEmbeddingClass(methodFullName)
		enviedClass = smell.split(';')[1]
		method = methodToNameMap[methodFullName]

		if embeddingClass not in MAP:
			MAP[embeddingClass] = {}

		if method not in MAP[embeddingClass]:
			MAP[embeddingClass][method] = []

		MAP[embeddingClass][method].append(enviedClass)

	
	return MAP


# Map normalized method names to true names (as it is in the source code)
def getMethodToNameMap(systemName):
	metFile = 'methodFiles/' + systemName + '.csv'

	methodToNameMap = {}
	with open(metFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			methodToNameMap[row['NORM_NAME']] = row['NAME']

	return methodToNameMap


if __name__ == "__main__":
	# Must create a directory TEMP/ containing all the systems repositories
	# at the considered snapshots before using this script

	subprocess.call('mkdir candidate_set/', shell=True)
	subprocess.call('mkdir sources/', shell=True)

	countCSV = 0
	countSmell = 0
	for system in systems:
		MAP = getSmells(system)
		dirName = 'sources/' + system['name'] + '/'
		subprocess.call('mkdir ' + dirName, shell=True)


		classPathFile = os.path.join(ROOT_DIR, 'data/entities/classes_all/' + system['name'] + '.csv')
		classToPathMap = {}
		with open(classPathFile, 'rb') as csvfile:
			reader = csv.DictReader(csvfile, delimiter=';')
			for row in reader:
				classToPathMap[row['Entity']] = row['Path']

		startURL = "https://github.com/antoineBarbez/feature_envy/blob/master/" + system['name'] + "/"

		for embeddingClass in MAP:
			embeddingClassPath = 'TEMP/' + system['name'] + '/' + classToPathMap[embeddingClass]
			subprocess.call('cp ' + embeddingClassPath + ' ' + dirName, shell=True)
			
			embeddingClassFileName = classToPathMap[embeddingClass].split('/')[-1]

			for method in MAP[embeddingClass]:
				for enviedClass in MAP[embeddingClass][method]:
					if countSmell%52 == 0:
						countCSV = countCSV + 1

						f = open('candidate_set/smells_' + str(countCSV) +'.csv', 'w')
						f.write('EMBED_CLASS,LINK_EMBED,METHOD,ENVIED_CLASS,LINK_ENVIED')
						f.write('\n')

					countSmell = countSmell + 1

					enviedClassFileName = classToPathMap[enviedClass].split('/')[-1]

					enviedClassSimpleName = enviedClass.split('.')[-1]
					pathInRepository = dirName + enviedClassSimpleName + '.java'

					if not os.path.isfile(pathInRepository):
						enviedClassPath = 'TEMP/' + system['name'] + '/' + classToPathMap[enviedClass]
						subprocess.call('cp ' + enviedClassPath + ' ' + dirName, shell=True)

					f.write('"' + embeddingClass + '"')
					f.write(',')
					f.write('"' + startURL + embeddingClassFileName + '"')
					f.write(',')
					f.write('"' + method.split('.')[-1] + '"')
					f.write(',')
					f.write('"' + enviedClass + '"')
					f.write(',')
					f.write('"' + startURL + enviedClassFileName + '"')
					f.write('\n')

