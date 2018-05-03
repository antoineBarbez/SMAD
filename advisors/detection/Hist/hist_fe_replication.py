from __future__ import print_function
from __future__ import division
#from sklearn.preprocessing import StandardScaler

#from reader import *
import sys
sys.path.insert(0, '../../../')
import reader as rdr

import progressbar
import math
import re
import csv
import dataConstruction.systems as systems
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, '../')
import evaluate

def normalizeSourceEntity(source_entity):
	m1 = re.match('(.+)\((.*)\)', source_entity)

	methodName = m1.group(1)
	parameters = m1.group(2)
	paramList = parameters.split(', ')

	normalizedParamList = []
	for param in paramList:
		normalizedParam = param.split('.')[-1]
		m2 = re.match('(\w*)\W*', normalizedParam)

		normalizedParamList.append(m2.group(1))

	normalizedParamList.sort()

	return methodName + '(' + ', '.join(normalizedParamList) + ')'

def feature_envy(systemName, alpha):
	historyFile = '../../../data/history/method_changes/' + systemName + '.csv'
	systemMethodsFile = '../../../data/instances/methods/' + systemName + '.csv'

	methods = []
	with open(systemMethodsFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			methods.append(row[0])

	methodsReverseDictionnary = {methods[i]: i for i in range(len(methods))}
	methodToClassDictionnary = {method:'.'.join(method.split('.')[:-1]) for method in methods}

	
	classes = ['.'.join(method.split('.')[:-1]) for method in methods]
	classes = list(set(classes))

	classesReverseDictionnary = {classes[i]: i for i in range(len(classes))}


	history_dict = rdr.readHistory(historyFile, "M")

	history = []
	commit = []
	snapshot = history_dict[0]['Snapshot']
	for i, change in enumerate(history_dict):
		if snapshot != change['Snapshot']:
			history.append(list(set(commit)))
			commit = []
			snapshot = change['Snapshot']

		if change['ChangeType'] == 'BODY_MODIFIED':
			commit.append(change['Method'])
		
		if i == len(history_dict)-1:
			history.append(list(set(commit)))



	bar = progressbar.ProgressBar(maxval=len(history), \
		widgets=['Performing cross validation: ' ,progressbar.Percentage()])
	bar.start()

	
	occurences = np.zeros((len(methods), len(classes)))
	for count, commit in enumerate(history):
		bar.update(count)
		for idx, method in enumerate(commit):
			if method in methods:
				coMethods = list(commit)
				del coMethods[idx]
				i = methodsReverseDictionnary[method]
				klasses = []
				for m in coMethods:
					if m in methods:
						klasses.append(methodToClassDictionnary[m])
				klasses = list(set(klasses))
				for klass in klasses:
					j = classesReverseDictionnary[klass]
					occurences[i,j] = occurences[i,j] + 1.

	bar.finish()

	ignore = []
	for i, m in enumerate(methods):
		j = classesReverseDictionnary[methodToClassDictionnary[m]]
		if occurences[i,j] == 0:
			#print('!!!' + methods[i])
			ignore.append(m)

		else:
			occurences[i,:] = occurences[i,:]/occurences[i,j]

	met, cla = np.where(occurences>alpha)

	smells = []
	string = ""
	for i in range(len(met)):
		'''string = methods[met[i]] + ';' + classes[cla[i]]'''
		if methods[met[i]] not in ignore:
			smells.append(methods[met[i]] + ';' + classes[cla[i]])
			string = string + str(occurences[met[i], cla[i]]) + ' '
		#print(occurences[met[i], cla[i]])

	#print(string)
	return smells



def test(systemName, alpha):
	print(systemName)
	trueFile = '../../../data/labels/Feature_envy/test/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			print(row[0])
			print(normalizeSourceEntity(row[0]))
			print(row[1])
			true.append(normalizeSourceEntity(row[0]) + ';' + row[1])

	# Get classes detected as God Classes
	detected = feature_envy(systemName, alpha)
	print(len(detected))
	detected = [d for d in detected if d.startswith('org.gjt.sp.jedit')]
	print(len(detected))
	#print(detected)
 
	pre = evaluate.precision(detected, true)
	rec = evaluate.recall(detected, true)
	f_m = evaluate.f_mesure(detected, true)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))

	return f_m



if __name__ == "__main__":
	systems = ['jedit']

	for system in systems:
		test(system, 0)
		print("")

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

	'''
	for system in systems.systems_git:
		roDictionnary = getRescaledOccurences(system['name'])

		print(roDictionnary)'''