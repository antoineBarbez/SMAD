from __future__ import print_function
from __future__ import division

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from reader import *
from evaluateModel import *

import os
import math

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def blob(systemName, alpha=8.0):
	historyFile = './data/history/class_changes/' + systemName + '.csv'
	systemClassesFile = './data/instances/classes/' + systemName + '.csv'

	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	reverseDictionnary = {classes[i]: i for i in xrange(len(classes))}
	changes = readHistory(historyFile)

	
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

	nbCommit = np.array([0 for _ in xrange(len(classes))])
	add = np.array([0 for _ in xrange(len(classes))])
	occurences = [0 for _ in xrange(len(classes))]
	for commit in reversed(data):
		for className in commit:
			if className in classes:
				idx = reverseDictionnary[className]
				add[idx] = 1

		nbCommit = nbCommit + add
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

	#print(nb)

	smells = []
	for i, nbOcc in enumerate(occurences):
		nbcommit = max(60,nbCommit[i])
		threshold = getThreshold(nbCommit[i], len(data), alpha)
		if nbOcc > threshold:
			#print(nbOcc, nbCommit[i])
			#print(classes[i])
			smells.append(classes[i])


	return smells

def getThreshold(nbCommitClass, nbCommit, alpha):
	x = nbCommit / 2 
	lim = min(400, x)
	nb = max(lim, nbCommitClass)

	return nb * alpha / 100

def getAlpha(systemName):
	systemClassesFile = './data/instances/classes/' + systemName + '.csv'

	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	nbClasses = len(classes)

	#return 9*math.exp(nbClasses*math.log(0.2)/800) + 1
	return 8

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

	results = []
	labels = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			if row[0] in true:
				labels.append([1,0])
			else:
				labels.append([0,1])

			if row[0] in detected:
				results.append([1,0])
			else:
				results.append([0,1])
	with tf.Session() as session: 

		pre = precision(np.array(results), np.array(labels))
		rec = recall(np.array(results), np.array(labels))
		f_m = f_mesure(np.array(results), np.array(labels))

		print('Precision :', "{0:.3f}".format(pre.eval()))
		print('Recall :', "{0:.3f}".format(rec.eval()))
		print('F-Mesure :', "{0:.3f}".format(f_m.eval()))

		return f_m.eval()








if __name__ == "__main__":
	systems = [
	"android-frameworks-opt-telephony",
	"android-frameworks-sdk",
	"android-platform-support",
	"apache-ant",
	"apache-tomcat",
	"jedit"
	]

	'''s = 0
	alphas = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0]
	als = []
	nbs = []
	for system in systems:
		systemClassesFile = './data/instances/classes/' + system + '.csv'
		classes = []
		with open(systemClassesFile, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')

			for row in reader:
				classes.append(row[0])

		nbs.append(len(classes))

		bestAL = 0
		bestFM = 0
		for alpha in alphas:
			f_m = test(system, alpha)
			if math.isnan(f_m):
				f_m = 0

			if f_m > bestFM:
				bestFM = f_m
				bestAL = alpha

		als.append(bestAL)

	plt.plot(nbs,als,'ro')
	plt.show()'''

	s = 0
	
	for system in systems:
		alpha = getAlpha(system)
		f_m = test(system, alpha)
		if math.isnan(f_m):
			f_m = 0
		s = s + f_m

	print(s/len(systems))
