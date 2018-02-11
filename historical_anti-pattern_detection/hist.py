from __future__ import print_function
from __future__ import division

from reader import *

def blob(systemName, alpha=8.0):
	historyFile = './data/systems_history/' + systemName + '.csv'
	systemClassesFile = './data/systems_methods/' + systemName + '.csv'

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



	for i, nbOcc in enumerate(occurences):
		threshold = nbCommit[i] * alpha / 100
		if nbOcc > threshold:
			print(classes[i])


def featureEnvy(systemName, Blob):



if __name__ == "__main__":
	blob("android-frameworks-opt-telephony")