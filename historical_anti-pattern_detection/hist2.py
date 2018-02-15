from __future__ import print_function
from __future__ import division

from reader import *

import math

def precision(detected, true):
	truePos = 0
	for className in detected:
		if className in true:
			truePos += 1 

	if len(true) == 0:
		return 0

	return truePos / len(true)

def recall(detected, true):
	truePos = 0
	for className in detected:
		if className in true:
			truePos += 1

	if len(detected) == 0:
		return 0 

	return truePos / len(detected)

def f_mesure(detected, true):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if (pre + rec) ==0:
		return 0

	return 2*pre*rec/(pre+rec)

def blob(systemName, alpha=8.0):
	historyFile = './data/history/class_changes/' + systemName + '.csv'
	systemClassesFile = './data/instances/classes/' + systemName + '.csv'

	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	reverseDictionnary = {classes[i]: i for i in xrange(len(classes))}
	changes = readHistory2(historyFile)


	data = []
	commit = []
	commitNumber = changes[0]['Snapshot']
	for i, change in enumerate(changes):
		if commitNumber != change['Snapshot']:
			data.append(set(commit))
			commit = []
			commitNumber = change['Snapshot']

		commit.append(change['Class'])
		if i == len(changes)-1:
			data.append(set(commit))

	nbCommit = [0 for _ in xrange(len(classes))]
	occurences = [0 for _ in xrange(len(classes))]
	for commit in data:
		nbCommit = [i+1 for i in nbCommit]
		if len(commit) > 1:
			for className in commit:
				if className in classes:
					idx = reverseDictionnary[className]
					occurences[idx] = occurences[idx] + 1

		else:
			className = list(commit)[0]
			if className in classes:
				idx = reverseDictionnary[className]
				nbCommit[idx] = nbCommit[idx] - 1


	smells = []
	for i, nbOcc in enumerate(occurences):
		threshold = nbCommit[i] * alpha / 100
		if nbOcc > threshold:
			#print(nbOcc, nbCommit[i])
			#print(classes[i])
			smells.append(classes[i])

	return smells



def test(systemName, alpha):
	print(systemName, alpha)
	trueFile = './data/labels/valid/' + systemName + '.csv'
	systemClassesFile = './data/instances/classes/' + systemName + '.csv'

	#Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			true.append(row[0])

	detected = blob(systemName, alpha)

	pre = precision(detected, true)
	rec = recall(detected, true)
	f_m = f_mesure(detected, true)

	#print('Precision :', "{0:.3f}".format(pre))
	#print('Recall :', "{0:.3f}".format(rec))
	#print('F-Mesure :', "{0:.3f}".format(f_m))

	return f_m



if __name__ == "__main__":
	test("ApacheAnt", 1.5)

	systems = [
	"android-frameworks-opt-telephony",
	"android-frameworks-sdk",
	"android-platform-support",
	"apache-ant",
	"apache-tomcat",
	"jedit"
	]

	s = 0
	alphas = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0]
	for system in systems:

		bestAL = 0
		bestFM = 0
		for alpha in alphas:
			f_m = test(system, int(alpha))
			print(f_m)
			if f_m == None:
				f_m = 0

			if f_m > bestFM:
				bestFM = f_m
				bestAL = alpha

		f_m = test(system, bestAL)
		print(f_m)
		
		if f_m == None:
			f_m = 0
		s = s + f_m

	print(s/len(systems))