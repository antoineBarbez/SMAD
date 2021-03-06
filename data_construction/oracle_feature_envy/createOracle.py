from context import ROOT_DIR

import utils.java_utils as java_utils
import numpy as np

import csv
import fnmatch
import os

# This script is used to automatically create the oracle from the answers collected by our survey.
# It implements a vote descision between the different answers for a same instance.
# For each system, it creates a file "data/antipatterns/feature_envy/system-name.txt" containing all the 
# instances of feature envy identified.

systems = [
		{
		'name' : 'android-frameworks-opt-telephony',
		'end_index': 62,
		},
		{
		'name' : 'android-platform-support',
		'end_index': 83,
		},
		{
		'name' : 'apache-ant',
		'end_index': 193,
		},
		{
		'name' : 'apache-tomcat',
		'end_index': 366,
		},
		{
		'name' : 'lucene',
		'end_index': 408,
		},
		{
		'name': 'argouml',
		'end_index': 552,
		},
		{
		'name' : 'jedit',
		'end_index': 650,
		},
		{
		'name' : 'xerces-2_7_0',
		'end_index': 779,
		}
	]

def getScore(answers):
	floatValues = []
	for answer in answers:
		if answer == 'Strongly approve':
			floatValues.append(1.0)
		elif answer == 'Weakly approve':
			floatValues.append(0.66)
		elif answer == 'Weakly disapprove':
			floatValues.append(0.33)
		elif answer == 'Strongly disapprove':
			floatValues.append(0.0)

	return np.mean(np.array(floatValues))

def getAnswers():
	answerDir = os.path.join(ROOT_DIR, 'data_construction', 'oracle_feature_envy','forms_answers')

	answers = []
	for path, dirs, files in os.walk(answerDir):
		for file in fnmatch.filter(sorted(files), '*.csv'):
			with open(os.path.join(path, file), 'r') as csvFile:
				reader = csv.DictReader(csvFile, delimiter=';')
				answers += [[row[key] for key in row if row[key] != 'METHOD_NAME'] for row in reader]

	return answers

def getCandidates():
	candidateDir = os.path.join(ROOT_DIR, 'data_construction', 'oracle_feature_envy' 'candidate_set')

	candidates = []
	for path, dirs, files in os.walk(candidateDir):
		for file in fnmatch.filter(sorted(files), '*.csv'):
			with open(os.path.join(path, file), 'r') as csvFile:
				reader = csv.DictReader(csvFile)
				candidates += [row['EMBED_CLASS'] + '.' + java_utils.normalizeMethodName(row['METHOD']) + ';' + row['ENVIED_CLASS'] for row in reader]

	return candidates


if __name__ == "__main__":
	startIndex = 0
	answers    = getAnswers()
	candidates = getCandidates()
	for system in systems:
		endIndex = system['end_index']
		smells = [candidates[i] for i in range(startIndex, endIndex) if getScore(answers[i]) >= 0.5]
		startIndex = endIndex

		labelFile = os.path.join(ROOT_DIR, 'data', 'antipatterns', 'feature_envy', system['name'] + '.txt')

		with open(labelFile, 'w') as file:
			for smell in smells:
				file.write(smell + '\n')


