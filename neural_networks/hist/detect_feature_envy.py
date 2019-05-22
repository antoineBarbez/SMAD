from __future__ import division
from context    import dataUtils, entityUtils

import numpy as np

import progressbar

def detect(systemName, alpha=2.6):
	# Get and prepare all data needed (methods, classes, history)
	methods = dataUtils.getMethods(systemName)
	methodToIndexMap = {m: i for i, m in enumerate(methods)}
	
	classes = dataUtils.getAllClasses(systemName)
	classToIndexMap = {c: i for i, c in enumerate(classes)}

	history = dataUtils.getHistory(systemName, "M")

	# Initialize progressbar
	bar = progressbar.ProgressBar(maxval=len(history), \
		widgets=['Analyzing ' + systemName + ' History : ' ,progressbar.Percentage()])
	bar.start()


	# Number of commits in which the methods are involved
	occ = np.zeros(len(methods))

	# Matrix representing co-occurences between methods and classes, i.e, the number of time each 
	# method of the system has been changed in commits involving methods of each class of the system.
	# For example, occurence[i, j] = 5 means that the ith method of the system have been involved
	# 5 times in commits involving methods of the jth class of the system.
	coOcc = np.zeros((len(methods), len(classes)))
	for count, commit in enumerate(history):
		bar.update(count)
		for idx, method in enumerate(commit):
			if method in methods:
				# Get method Index 
				i = methodToIndexMap[method]

				# Increase nb occurences of the method
				occ[i] = occ[i] + 1

				# Get the other methods that changed together with the method in this commit
				coMethods = list(commit)
				del coMethods[idx]

				# Get the classes where these "other methods" are implemented
				klasses = []
				for m in coMethods:
					embeddingClass = entityUtils.getEmbeddingClass(m)
					if embeddingClass in classes:
						klasses.append(embeddingClass)
				klasses = list(set(klasses))

				# For each of these classes increase the corresponding value in the occurences matrix
				for klass in klasses:
					j = classToIndexMap[klass]
					coOcc[i,j] = coOcc[i,j] + 1.

	bar.finish()

	ignore = []
	for i, m in enumerate(methods):
		if occ[i] == 0:
			ignore.append(m)

		j = classToIndexMap[entityUtils.getEmbeddingClass(m)]
		if coOcc[i,j] == 0:
			coOcc[i,j] = 0.5
		
		coOcc[i,:] = coOcc[i,:]/coOcc[i,j]

	smellsMap = {}
	for i, j in zip(*np.where(coOcc>alpha)):
		if methods[i] not in ignore: 
			if methods[i] in smellsMap:
				smellsMap[methods[i]] += [classes[j]]
			else:
				smellsMap[methods[i]] = [classes[j]]
	
	smells = []
	for m in smellsMap:
		if len(smellsMap[m]) <= 2:
			for c in smellsMap[m]:
				smells.append(m + ';' + c)

		
	return smells
