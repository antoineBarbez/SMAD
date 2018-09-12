from __future__ import division
from context    import reader, entityUtils

import numpy as np

import progressbar



def getSmells(systemName, alpha):
	methods = reader.getMethods(systemName)
	methodsReverseDictionnary = {methods[i]: i for i in range(len(methods))}
	
	classes = reader.getAllClasses(systemName)
	classesReverseDictionnary = {classes[i]: i for i in range(len(classes))}

	history_dict = reader.getHistory(systemName, "M")

	history = []
	commit = []
	snapshot = history_dict[0]['Snapshot']
	for i, change in enumerate(history_dict):
		if snapshot != change['Snapshot']:
			history.append(list(set(commit)))
			commit = []
			snapshot = change['Snapshot']

		commit.append(change['Entity'])
		
		if i == len(history_dict)-1:
			history.append(list(set(commit)))



	bar = progressbar.ProgressBar(maxval=len(history), \
		widgets=['Hist feature envy replication: ' ,progressbar.Percentage()])
	bar.start()

	nbOcc = np.zeros(len(methods))
	occurences = np.zeros((len(methods), len(classes)))
	for count, commit in enumerate(history):
		bar.update(count)
		for idx, method in enumerate(commit):
			if method in methods:
				coMethods = list(commit)
				del coMethods[idx]
				i = methodsReverseDictionnary[method]
				nbOcc[i] = nbOcc[i] + 1
				klasses = []
				for m in coMethods:
					embeddingClass =entityUtils.getEmbeddingClass(m)
					if embeddingClass in classes:
						klasses.append(embeddingClass)
				klasses = list(set(klasses))
				for klass in klasses:
					j = classesReverseDictionnary[klass]
					occurences[i,j] = occurences[i,j] + 1.

	bar.finish()

	ignore = []
	for i, m in enumerate(methods):
		if nbOcc[i] == 0:
			ignore.append(m)

		j = classesReverseDictionnary[entityUtils.getEmbeddingClass(m)]
		if occurences[i,j] == 0:
			occurences[i,j] = 0.5
		
		occurences[i,:] = occurences[i,:]/occurences[i,j]

	met, cla = np.where(occurences>alpha)

	smellsMap = {}
	for i in range(len(met)):
		if methods[met[i]] not in ignore: 
			if methods[met[i]] in smellsMap:
				smellsMap[methods[met[i]]] += [classes[cla[i]]]
			else:
				smellsMap[methods[met[i]]] = [classes[cla[i]]]

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