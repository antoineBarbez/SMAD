from __future__ import print_function
from __future__ import division

import csv
import os
import sys
import fnmatch
import pickle

import numpy as np

''' This file contains all the methods that we will use to extract the data from 
	the differents csv files (historical information, anti-pattern occurences...)'''

def readHistory(csvFile):
	with open(csvFile, 'rb') as csvfile:
		#print('start readind file :', csvFile)
		reader = csv.DictReader(csvfile, delimiter=';')
		changes = []
		for row in reader:
			if row['Entity'] == 'METHOD':
				code = row['Code'].split('.')
				code.pop()
				className = '.'.join(code)

				change = {}
				change['Snapshot'] = row['Snapshot']
				change['Class'] = className
				changes.append(change)

			if row['Entity'] == 'CLASS':
				change = {}
				change['Snapshot'] = row['Snapshot']
				change['Class'] = row['Code']
				changes.append(change)

		return changes


#return the co-occurence matrix of the different classes
def getCoocMatrix(changes):
	print('start getting cooccurence matrix...')
	data = []
	classOcc = []
	commit = []
	commitNumber = changes[0]['Snapshot']
	for i, change in enumerate(changes):
		classOcc.append(change['Class'])
		if commitNumber != change['Snapshot']:
			data.append(commit)
			commit = []
			commitNumber = change['Snapshot']

		commit.append(change['Class'])
		if i == len(changes)-1:
			data.append(commit)

	classes = list(set(classOcc))
	size = len(classes)
	reverseDictionnary = {classes[i]: i for i in xrange(size)}

	coocMatrix = np.zeros((size,size), dtype=np.int16)

	#TODO this last part is very long at execution, try to reduce it !
	for commit in data:
		oneHotCommit = np.zeros((size,1), dtype=np.int16)
		for className in set(commit):
			oneHotCommit[reverseDictionnary[className],0] = 1;

		coocMatrix += oneHotCommit.dot(oneHotCommit.T)
	return reverseDictionnary , coocMatrix


#only use for test purpose
def getReverseDictionnary(csvFile):
	changes = readHistory(csvFile)

	data = []
	classOcc = []
	commit = []
	commitNumber = changes[0]['Snapshot']
	for i, change in enumerate(changes):
		classOcc.append(change['Class'])
		if commitNumber != change['Snapshot']:
			data.append(commit)
			commit = []
			commitNumber = change['Snapshot']

		commit.append(change['Class'])
		if i == len(changes)-1:
			data.append(commit)

	classes = list(set(classOcc))
	size = len(classes)
	reverseDictionnary = {classes[i]: i for i in xrange(size)}

	return reverseDictionnary


def saveCoocMatrices():
	for path,dirs,files in os.walk('./data/systems_history'):

		for f in fnmatch.filter(files,'*.csv'):
			historyFile = './data/systems_history/' + f
			fName = f.split('.')[0]
			coocFile = './data/co-occurence_matrices/' + fName + '.pickle'

			changes = readHistory(historyFile)
			reverseDictionnary , coocMatrix = getCoocMatrix(changes)
			data = (reverseDictionnary , coocMatrix)

			with open(coocFile, 'wb') as file:
				pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)


#return the conditional probability matrix of the different classes
def getCPM(coocMatrix):
	'''concidering ci=True if the class i change in a commit ,
	CPM(i,j) = P(cj|ci) = coocMatrix(i,j)/coocMatrix(i,i)'''
	size = len(coocMatrix)
	eye = np.identity(size)
	ones = np.ones(size).reshape(size,1)

	#DIV is a matrix which's column values are 1/coocMatrix(i,i)
	DIV = ones.dot(np.divide(ones,(coocMatrix*eye).dot(ones)).T)
	CPM = coocMatrix*DIV

	return CPM

''' return instances and labels that will be used to train some models later.
	The instances represents classes of a software 
	and are of the form of a (nbClasses - 1 , 2) matrix where 
	nbClasses is the number of classes in the given system.

	concidering I the instance corresponding to the ith class (ci) of a system,
	I(j,1) = P(ci | cj) and I(j, 2) = P(cj | ci)
	
'''
def constructDataset():
	instances = []
	labels = np.array([])

	for path,dirs,files in os.walk('./data/co-occurence_matrices'):

		for f in fnmatch.filter(files,'*.pickle'):
			fileName = f.split('.')[0]
			coocFile = './data/co-occurence_matrices/' + f
			blobOccurencesFile = './data/blob/' + fileName + '.csv'

			with open(coocFile, 'r') as open_file:
				reverseDictionnary , coocMatrix = pickle.load(open_file)
				CPM = getCPM(coocMatrix)

			blobOccurences = np.zeros(len(reverseDictionnary))

			with open(blobOccurencesFile, 'rb') as csvfile:
				reader = csv.reader(csvfile, delimiter=';')

				blobOccurences = np.zeros(len(reverseDictionnary))
				for row in reader:
					blobOccurences[reverseDictionnary[row[0]]] = 1

				labels = np.append(labels, blobOccurences)

			for i in range(len(reverseDictionnary)):
				c1 = CPM[:,i]
				c2 = CPM[i,:]
				c1 = np.delete(c1,i)
				c2 = np.delete(c2,i)

				c = np.append(c1,c2).reshape(2,len(c1)).T
				instances.append(c)

	return instances , labels


#used to test an idea, not important ....
def read(csvFile):
	with open(csvFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		changes = []
		for row in reader:
			if row['Entity'] == 'METHOD':
				change = {}
				change['Snapshot'] = row['Snapshot']
				change['Methode'] = row['Code']
				changes.append(change)

		return changes

def data2Text(csvFile):
	changes = read(csvFile)

	f = open('data.txt','a')

	commit = ''
	commitNumber = changes[0]['Snapshot']
	for change in changes:
		if commitNumber != change['Snapshot']:
			f.write(commit + '\n')
			commit = ''
			commitNumber = change['Snapshot']

		commit = commit + ' ' +change['Methode']

	f.close()


if __name__ == "__main__":
	'''changes = [
		{'Snapshot': '1', 'Class':'a'},
		{'Snapshot': '1', 'Class':'b'},
		{'Snapshot': '2', 'Class':'a'},
		{'Snapshot': '3', 'Class':'a'},
		{'Snapshot': '3', 'Class':'a'},
		{'Snapshot': '3', 'Class':'c'},
		{'Snapshot': '3', 'Class':'b'},
		{'Snapshot': '4', 'Class':'d'},
		{'Snapshot': '4', 'Class':'b'},
		{'Snapshot': '4', 'Class':'c'},
		{'Snapshot': '5', 'Class':'d'},
		{'Snapshot': '6', 'Class':'a'},
		{'Snapshot': '6', 'Class':'a'},
		{'Snapshot': '6', 'Class':'b'},
		{'Snapshot': '7', 'Class':'b'},
		{'Snapshot': '7', 'Class':'c'},
	]

	reverseDictionnary , coocMatrix = getCoocMatrix(changes)
	print(reverseDictionnary)
	print(coocMatrix)
	data = (reverseDictionnary , coocMatrix)

	with open('./data/co-occurence_matrix/test.pickle', 'wb') as file:
		pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

	with open('./data/co-occurence_matrix/test.pickle', 'r') as open_file:
            rd , cM = pickle.load(open_file)
            print(rd)
            print(cM)'''

	#x , y = constructDataset()
	#print(x[1733].shape)
	#print(y.shape)
	#print(y.sum())


	


