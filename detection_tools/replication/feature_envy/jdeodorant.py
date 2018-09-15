from __future__ import division
from context    import ROOT_DIR, dataUtils, entityUtils



def getSmells(systemName):
	JDFEFile = ROOT_DIR + '/detection_tools/metrics_files/feature_envy/JDeodorant/' + systemName + '.txt'

	methods = dataUtils.getMethods(systemName)
	smells = []
	with open(JDFEFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				source_entity = line.split('\t')[1].replace('::', '.')
				source_entity = source_entity.split(':')[0]
				source_entity = entityUtils.normalizeMethodName(source_entity)
				target_class = line.split('\t')[2]

				if source_entity in methods:
					smells.append(source_entity + ';' + target_class)
			i = i + 1

	return list(set(smells))

'''
def test(systemName):
	print(systemName)
	trueFile = '../../../data/labels/Feature_envy/test/' + systemName + '.csv'

	# Get Smells occurences
	true = []
	with open(trueFile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		for row in reader:
			print(row[0])
			true.append(normalizeSourceEntity(row[0]) + ';' + row[1])

	# Get classes detected as God Classes
	detected = feature_envy(systemName)
	print(detected)
 
	pre = evaluate.precision(detected, true)
	rec = evaluate.recall(detected, true)
	f_m = evaluate.f_mesure(detected, true)

	print('Precision :' + str(pre))
	print('Recall    :' + str(rec))
	print('F-Mesure  :' + str(f_m))

	return f_m

'''
if __name__ == "__main__":
	systems = ['android-frameworks-opt-telephony', 'android-platform-support', 'apache-ant', 'apache-tomcat', 'lucene', 'argouml', 'jedit', 'xerces-2_7_0']
	for system in systems:
		nbClass = feature_envy(system)
		print(system + ': ' + str(len(nbClass)))


	'''systems = ['apache-tomcat', 'jedit', 'android-platform-support', 'apache-ant']

	for system in systems:
		test(system)
		print("")'''

	print(len(feature_envy('jedit')))
