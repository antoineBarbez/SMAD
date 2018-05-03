from __future__ import division

import numpy as np
import matplotlib.pyplot as plt

import csv
import progressbar
import sys

sys.path.insert(0, '../')
import evaluate

sys.path.insert(0, '../../../')
import reader as rdr

''' This file is just used to obtain DECOR detection results on the test set'''


def blob(systemName, alpha=8.0):
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



def test(systemName, alpha):
	print(systemName, alpha)
	trueFile = '../../../data/labels/Blob/hand_validated/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			true.append(row[0])

	# Get classes detected as God Classes
	detected = blob(systemName, alpha)
	print(detected)
 
	pre = evaluate.precision(detected, true)
	rec = evaluate.recall(detected, true)
	f_m = evaluate.f_mesure(detected, true)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))

	return f_m

def overall(systems):

	overallSmells = []
	overallTrue = []
	for system in systems:
		trueFile = '../../../data/labels/Blob/hand_validated/' + system + '.csv'

		with open(trueFile, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')

			for row in reader:
				overallTrue.append(row[0])

		smells = blob(system)

		for s in smells:
			overallSmells.append(s)

	pre = evaluate.precision(overallSmells, overallTrue)
	rec = evaluate.recall(overallSmells, overallTrue)
	f_m = evaluate.f_mesure(overallSmells, overallTrue)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))



if __name__ == "__main__":
	systems = ['apache-tomcat', 'jedit', 'android-platform-support']

	for system in systems:
		r = test(system, 8.0)
		print("")

	print("OVERALL")
	overall(systems)



	# Uncomment to perform alpha calibration. 
	# Best alpha: 10.0
	'''
	num_tests = 200

	bar = progressbar.ProgressBar(maxval=num_tests, \
		widgets=['Performing calibration of alpha: ' ,progressbar.Percentage()])
	bar.start()

	alphas = 0 + 0.1*np.array(range(num_tests))
	f_m = []
	std = []
	i = 0
	for i, alpha in enumerate(alphas):
		bar.update(i)

		results = []
		for systemName in systems:
			results.append(test(systemName, alpha))

		f_m.append(np.mean(np.array(results)))
		std.append(np.std(np.array(results)))

	bar.finish()

	plt.plot(alphas, f_m, 'ro', alphas, std)
	plt.show()'''

