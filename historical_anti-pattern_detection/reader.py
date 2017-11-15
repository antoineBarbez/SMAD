from __future__ import print_function
from __future__ import division

import csv
import os
import sys
import fnmatch

import numpy as np


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

def readHistory(csvFile):
	with open(csvFile, 'rb') as csvfile:
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

	coocMatrix = np.zeros((size,size), dtype=np.int32)
	
	for commit in data:
		oneHotCommit = np.zeros(size, dtype=np.int32)
		for className in set(commit):
			oneHotCommit[reverseDictionnary[className]] = 1;

		c = oneHotCommit.reshape(size,1)
		coocMatrix += c.dot(c.T)

	return coocMatrix

#return the conditional probability matrix of the different classes
def getCPM(csvFile):
	changes = readHistory(csvFile)
	coocMatrix = getCoocMatrix(changes)

	'''concidering ci=True if the class i change in a commit ,
	CPM(i,j) = P(cj|ci) = coocMatrix(i,j)/coocMatrix(i,i)'''
	size = len(coocMatrix)
	eye = np.identity(size)
	ones = np.ones(size).reshape(size,1)

	#DIV is a matrix which's column values are 1/coocMatrix(i,i)
	DIV = ones.dot(np.divide(ones,(coocMatrix*eye).dot(ones)).T)
	CPM = coocMatrix*DIV

	return CPM


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
	'''for path,dirs,files in os.walk('./systems_history'):
		for f in fnmatch.filter(files,'*.csv'):
			fullname = os.path.abspath(os.path.join(path,f))
			changes = read(fullname)

			snapshots = []
			methods = []

			for change in changes:
				snapshots.append(change['Snapshot'])
				methods.append(change['Methode'])

			ratio = (len(methods)/len(set(methods)))
			print('system name :', f)
			print('nb snapshot :',len(set(snapshots)))
			print('methods :', ratio)'''

	#data2Text('./systems_history/frameworks-base.csv')

	'''changes = [
		{'Snapshot': '1', 'Class':'a'},
		{'Snapshot': '1', 'Class':'b'},
		{'Snapshot': '2', 'Class':'a'},
		{'Snapshot': '3', 'Class':'a'},
		{'Snapshot': '3', 'Class':'a'},
		{'Snapshot': '3', 'Class':'c'},
		{'Snapshot': '3', 'Class':'b'},
		{'Snapshot': '4', 'Class':'b'},
		{'Snapshot': '4', 'Class':'b'},
		{'Snapshot': '4', 'Class':'c'},
	]

	coocMatrix = getCoocMatrix(changes)'''
	CPM = getCPM('./data/systems_history/frameworks-support.csv')
	print(CPM)

	


