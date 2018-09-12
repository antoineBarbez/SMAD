from __future__ import division

import numpy as np

import csv
import progressbar
import sys

sys.path.insert(0, '../')
import evaluate

sys.path.insert(0, '../../../')
import reader as rdr


# Merge detection results of DECOR, JDeodorant and Hist by vote 

def blob_DECOR(systemName):
	decorMetricsFile = '../../results/Decor/Blob/' + systemName + '.csv'
	
	smells = []
	with open(decorMetricsFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			nmdNad      = float(row['NMD+NAD'])
			nmdNadBound = float(row['nmdNadBound'])
			lcom5       = float(row['LCOM5'])
			lcom5Bound  = float(row['lcom5Bound'])
			cc          = int(row['ControllerClass'] )
			nbDataClass = int(row['nbDataClass'])

			if nbDataClass > 0:
				if nmdNad/nmdNadBound > 1:
					smells.append(row['ClassName'])

				elif lcom5/lcom5Bound > 1:
					smells.append(row['ClassName']) 

				elif cc == 1:
					smells.append(row['ClassName'])

	return smells


def blob_HIST(systemName, alpha=8.0):
	historyFile = '../../../data/history/class_changes/' + systemName + '.csv'
	systemClassesFile = '../../../data/instances/classes/' + systemName + '.csv'

	# Get the name of all the classes in the system's current version (the version used for the study)
	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	reverseDictionnary = {classes[i]: i for i in xrange(len(classes))}


	# Create an history list containing the names of the classes that changed in each commit.
	# For example, if class1 and class3 changed in the first commit, 
	# and class1, class2, class3 changed in the second commit, etc ...
	# The history list will be [[class1, Class3], [class1, class2, class3], ...]

	history_dict = rdr.readHistory(historyFile, "C")

	history = []
	commit = []
	snapshot = history_dict[0]['Snapshot']
	for i, change in enumerate(history_dict):
		if snapshot != change['Snapshot']:
			history.append(list(set(commit)))
			commit = []
			snapshot = change['Snapshot']

		commit.append(change['Class'])
		
		if i == len(history_dict)-1:
			history.append(list(set(commit)))


	# Compute for each class in classes, the number of commit involving at least another class,
	# and the number of occurences in this set of commit.
	nbCommit = np.array([0 for _ in range(len(classes))])
	occurences = [0 for _ in range(len(classes))]
	for commit in history:
		nbCommit = [n+1 for n in nbCommit]

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


	# Return all the classes 'involved in more than alpha% of commits involving at least another class'
	smells = []
	for i, nbOcc in enumerate(occurences):
		threshold = nbCommit[i]*alpha/100
		if nbOcc > threshold:
			smells.append(classes[i])


	return smells


def blob_JD(systemName):
	JDBlobFile = '../../results/JDeodorant/Blob/' + systemName + '.txt'
	
	smells = []
	with open(JDBlobFile, 'r') as file:
		for line in file:
			className = line.split()[0]
			smells.append(className)

	return list(set(smells))


# Perform vote between DECOR, JDeodorant and Hist.
# k: Minimum nomber of vote needed to detect a God Class
def vote(systemName, k):
	systemClassesFile = '../../../data/instances/classes/' + systemName + '.csv'


	decorSmells = blob_DECOR(systemName)
	histSmells = blob_HIST(systemName)
	jdSmells = blob_JD(systemName)


	classes = []
	with open(systemClassesFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			classes.append(row[0])

	smells = []
	for className in classes:
		count = 0

		if className in decorSmells:
			count = count + 1

		if className in histSmells:
			count = count + 1

		if className in jdSmells:
			count = count + 1


		if count >= k:
			smells.append(className)


	return smells



def test(systemName, k):
	print(systemName)
	trueFile = '../../../data/labels/Blob/hand_validated/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			true.append(row[0])

	# Get classes detected as God Classes
	detected = vote(systemName, k)
 
	pre = evaluate.precision(detected, true)
	rec = evaluate.recall(detected, true)
	f_m = evaluate.f_mesure(detected, true)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))

	return pre, rec, f_m


def overall(systems , k):

	overallSmells = []
	overallTrue = []
	for system in systems:
		trueFile = '../../../data/labels/Blob/hand_validated/' + system + '.csv'

		with open(trueFile, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')

			for row in reader:
				overallTrue.append(row[0])

		smells = vote(system, k)

		for s in smells:
			overallSmells.append(s)

	pre = evaluate.precision(overallSmells, overallTrue)
	rec = evaluate.recall(overallSmells, overallTrue)
	f_m = evaluate.f_mesure(overallSmells, overallTrue)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))


if __name__ == "__main__":

	ktest = 3

	systems = ['apache-tomcat', 'jedit', 'android-platform-support']

	precs = []
	recs = []
	f_ms = []


	for system in systems:
		p, r, f = test(system, ktest)

		precs.append(p)
		recs.append(r)
		f_ms.append(f)
		print("")

	precision = np.mean(np.array(precs), axis=0)
	recall = np.mean(np.array(recs), axis=0)
	f_mesure = np.mean(np.array(f_ms), axis=0)


	print("MEAN")
	print('Precision :' + str(precision))
	print('Recall    :' + str(recall))
	print('F-Mesure  :' + str(f_mesure))


	print()
	print("OVERALL")
	overall(systems, ktest)