from __future__ import division

import csv
import sys

sys.path.insert(0, '../')
import evaluate

''' This file is just used to obtain JDeodorant detection results on the test set'''

def blob(systemName):
	JDBlobFile = '../../results/JDeodorant/Blob/' + systemName + '.txt'
	
	smells = []
	with open(JDBlobFile, 'r') as file:
		for line in file:
			className = line.split()[0]
			smells.append(className)

	return list(set(smells))




def test(systemName):
	print(systemName)
	trueFile = '../../../data/labels/Blob/hand_validated/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			true.append(row[0])

	# Get classes detected as God Classes
	detected = blob(systemName)
 
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
		r = test(system)
		print("")

	print("OVERALL")
	overall(systems)