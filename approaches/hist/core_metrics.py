from context import ROOT_DIR

import utils.data_utils as data_utils
import utils.entity_utils as entity_utils
import numpy as np

import csv
import os
import progressbar

def getGCCoreMetrics(systemName):
	# Get the class history of the system
	history = getHistory(systemName, "C")

	#Get the names of all the classes involved in the system's history 
	classes = data_utils.getClasses(systemName)
	classToIndexMap = {c: i for i, c in enumerate(classes)}
	
	# For each class, number of commit involving at least another class
	nbCommit = np.zeros(len(classes))
	
	# For each class, number of changes in commits involving at least another class
	occurences = np.zeros(len(classes))

	for commit in history:
		nbCommit += 1

		if len(commit) > 1:
			for className in commit:
				if className in classes:
					idx = classToIndexMap[className]
					occurences[idx] += 1

		else:
			className = commit[0]
			if className in classes:
				idx = classToIndexMap[className]
				nbCommit[idx] -= 1

	ratio = occurences/nbCommit

	return {classes[i]: [ratio[i]] for i in range(len(classes))}


def getFECoreMetrics(systemName):
	# Get all data needed
	methods = data_utils.getMethods(systemName)
	methodToIndexMap = {m: i for i, m in enumerate(methods)}

	classes = data_utils.getAllClasses(systemName)
	classToIndexMap = {c: i for i, c in enumerate(classes)}
	
	co_occ_matrix = getCoOccurrenceMatrix(systemName)

	for i, m in enumerate(methods):
		# Get the number of co-occurrences with methods of its own class (i.e., the embedding class)
		idx_embedding_class = classToIndexMap[entity_utils.getEmbeddingClass(m)]
		nb_co_occ_ec = 0.5 if co_occ_matrix[i, idx_embedding_class] == 0 else co_occ_matrix[i, idx_embedding_class]

		co_occ_matrix[i,:] = co_occ_matrix[i,:]/nb_co_occ_ec

	dictionnary= {}
	entities = data_utils.getEntities('feature_envy', systemName)
	for entityName in entities:
		method = entityName.split(';')[0]
		enviedClass = entityName.split(';')[1]
		i = methodToIndexMap[method]
		j = classToIndexMap[enviedClass]
		dictionnary[entityName] = [co_occ_matrix[i,j]]

	return dictionnary

def getHistory(systemName, granularity):
	'''
	Returns a list containing the names of the entities
	(i.e, classes or methods) that changed at each commit.

	For example, if entity1 and entity3 changed in the first commit, 
	and entity1, entity2, entity3 changed in the second commit, etc ...
	The history list will be [[entity1, entity3], [entity1, entity2, entity3], ...]
	
	args:
		granularity: either "C" or "M" for class or method history respectively.
	'''

	dirName = {"C": "class_changes", "M": "method_changes"}
	historyFile = os.path.join(ROOT_DIR, 'data', 'history', dirName[granularity], systemName + '.csv')
	with open(historyFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		rawHistory = [{key: row[key] for key in row} for row in reader]

		history  = []
		commit   = []
		snapshot = rawHistory[0]['Snapshot']
		for i, change in enumerate(rawHistory):
			if snapshot != change['Snapshot']:
				history.append(list(set(commit)))
				commit = []
				snapshot = change['Snapshot']

			commit.append(change['Entity'])

			if i == len(rawHistory)-1:
				history.append(list(set(commit)))

	return history

def getCoOccurrenceMatrix(systemName):
	'''
	Matrix representing co-occurences between methods and classes, i.e, the number of time each 
	methods of the system has been changed in commits involving methods of each class of the system.
	
	For example, coOcc[i, j] = 5 means that the ith method of the system have been involved
	5 times in commits involving methods of the jth class of the system.
	'''

	# Get and prepare all data needed (methods, classes, history)
	methods = data_utils.getMethods(systemName)
	methodToIndexMap = {m: i for i, m in enumerate(methods)}

	classes = data_utils.getAllClasses(systemName)
	classToIndexMap = {c: i for i, c in enumerate(classes)}

	history = getHistory(systemName, "M")

	# Initialize progressbar
	bar = progressbar.ProgressBar(maxval=len(history), \
	    widgets=['Building co-occurrences matrix for ' + systemName + ': ' ,progressbar.Percentage()])
	bar.start()

	coOcc = np.zeros((len(methods), len(classes)))
	for count, commit in enumerate(history):
		bar.update(count)
		for idx, method in enumerate(commit):
			if method in methods:
				# Get method Index 
				i = methodToIndexMap[method]

				# Get the other methods that changed together with the method in this commit
				coMethods = list(commit)
				del coMethods[idx]

				# Get the classes where these "other methods" are implemented
				klasses = []
				for m in coMethods:
					embeddingClass = entity_utils.getEmbeddingClass(m)
					if embeddingClass in classes:
						klasses.append(embeddingClass)

				klasses = list(set(klasses))
				# For each of these classes increase the corresponding value in the co-occurrence matrix
				for klass in klasses:
					j = classToIndexMap[klass]
					coOcc[i,j] += 1.
	bar.finish()

	return coOcc