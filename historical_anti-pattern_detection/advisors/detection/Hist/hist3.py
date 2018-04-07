from __future__ import print_function
from __future__ import division
from sklearn.preprocessing import StandardScaler

#from reader import *
import reader as r

import math
import csv
import dataConstruction.systems as systems
import matplotlib.pyplot as plt
import numpy as np

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

def f_mesure(detected, true, alpha):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if (pre + rec) ==0:
		return 0

	return pre*rec/(alpha*rec + (1-alpha)*pre)

	#return 2*pre*rec/(pre+rec)

def getRescaledOccurences(systemName):
	historyFile = './data/history/class_changes/' + systemName + '.csv'
	systemClassesFile = './data/instances/classes/' + systemName + '.csv'

	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	reverseDictionnary = {classes[i]: i for i in range(len(classes))}
	changes = r.readHistory2(historyFile)


	data = []
	#totalClasses = []
	commit = []
	commitNumber = changes[0]['Snapshot']
	for i, change in enumerate(changes):
		if commitNumber != change['Snapshot']:
			data.append(set(commit))
			#totalClasses = totalClasses + list(set(commit))
			commit = []
			commitNumber = change['Snapshot']

		commit.append(change['Class'])

		if i == len(changes)-1:
			data.append(set(commit))
			#totalClasses = totalClasses + list(set(commit))

	#totalClasses = list(set(totalClasses))
	#totalReverseDictionnary = {totalClasses[i]: i for i in xrange(len(totalClasses))}

	nbCommit = len(data)
	occurences = [0 for _ in range(len(classes))]
	#totalOccurences = [0 for _ in xrange(len(totalClasses))]
	for commit in data:
		for className in commit:
			#tidx = totalReverseDictionnary[className]
			#totalOccurences[tidx] = totalOccurences[tidx] + 1
			if className in classes:
				idx = reverseDictionnary[className]
				occurences[idx] = occurences[idx] + 1

	#occurences = np.array(occurences).astype(float)
	
	#scaler = StandardScaler()
	#scaler.fit(occurences.reshape(-1, 1))
	#rescaledOcc = scaler.transform(occurences.reshape(-1, 1))

	#return {classes[i]:rescaledOcc.reshape(-1)[i] for i in range(len(classes))}

	return {classes[i]: occurences[i] for i in range(len(classes))}


def blob(systemName, alpha):
	roDictionnary = getRescaledOccurences(systemName)

	smells = []
	for className in roDictionnary:
		if roDictionnary[className] > alpha:
			smells.append(className)

	return smells



def test(systemName, alpha):
	#print(systemName, alpha)
	trueFile = './data/labels/Blob/test/' + systemName + '.csv'
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
	f_m = f_mesure(detected, true, 0.5)

	#print('Precision :', "{0:.3f}".format(pre))
	#print('Recall :', "{0:.3f}".format(rec))
	#print('F-Mesure :', "{0:.3f}".format(f_m))

	return f_m



if __name__ == "__main__":

	'''for system in systems.hist:
		f_m = test(system['name'], 2.3)
		print(system['name'] + " : " + str(f_m))'''

	
	'''alphas = 0.4 + 0.1*np.array(range(50))
	f_m = []
	std = []
	i = 0
	for alpha in alphas:
		i = i + 1
		print (str(i))
		s = []
		for system in systems.test:
			s.append(test(system['name'], alpha))

		f_m.append(np.mean(s))
		std.append(np.std(s))

	plt.plot(alphas, f_m, 'ro', alphas, std)
	plt.show()'''


	'''
	s = 0
	alphas = 1 + 0.1*np.array(range(60))
	for system in systems.test:
		print(system['name'])

		bestAL = 0
		bestFM = 0
		f_m = 0
		for alpha in alphas:
			f_m = test(system['name'], alpha)
			#print(f_m)
			if f_m == None:
				f_m = 0

			if f_m > bestFM:
				bestFM = f_m
				bestAL = alpha

		f_m = test(system['name'], bestAL)
		print(f_m)
		print(bestAL)
		
		if f_m == None:
			f_m = 0
		s = s + f_m

	print(s/len(systems.test))'''

	for system in systems.systems_git:
		roDictionnary = getRescaledOccurences(system['name'])

		print(roDictionnary)