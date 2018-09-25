from __future__ import division
from context    import dataUtils, entityUtils

import numpy as np

import progressbar



def getSmells(systemName, alpha=2.0):
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
	# methods of the system has been changed in commits involving methods of each class of the system.
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

'''
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

'''

if __name__ == "__main__":
	smel = feature_envy('android-frameworks-opt-telephony', 1.8)
	print(len(smel))
	print(smel)

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