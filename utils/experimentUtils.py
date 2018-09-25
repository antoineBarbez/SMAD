from __future__               import division
#from context                  import cm
#from sklearn.preprocessing    import StandardScaler

import numpy as np

import dataUtils


# Outputs instances (i.e, class for God Class and method;enviedClass for Feature Envy) 
# detected using a vote over various tools outputs.
# tools_outputs: list containing the lists of instances detected by each tool
# k: mininum number of tools agreement to detect an instance
def vote(tools_outputs, k):
	assert k <= len(tools_outputs), "k can't be greater than the number of tools"

	# Map instances to the number of tools that have detected this instance
	instanceToNbToolMap = {}
	for detected in tools_outputs:
		for instance in detected:
			if instance in instanceToNbToolMap:
				instanceToNbToolMap[instance] = instanceToNbToolMap[instance] + 1
			else:
				instanceToNbToolMap[instance] = 1

	return [instance for instance in instanceToNbToolMap if instanceToNbToolMap[instance] >= k]


def recall(detected, true):	
	truePositive = [entity for entity in detected if entity in true]

	if len(true) == 0:
		return float('nan')

	return len(truePositive) / len(true)

def precision(detected, true):
	truePositive = [entity for entity in detected if entity in true]

	if len(detected) == 0:
		#return float('nan')
		return 0.0

	return len(truePositive) / len(detected)

def f_measure(detected, true, alpha=0.5):
	pre = precision(detected, true)
	rec = recall(detected, true)

	if ((pre == 0) & (rec == 0)):
		return 0.0

	return pre*rec/(alpha*rec + (1-alpha)*pre)


#### Instances and labels getters in vector form (for neural-network use) ###


# Get labels in vector form for a given system
# antipattern in ['god_class', 'feature_envy']
def getLabelVectors(systemName, antipattern):
	true = dataUtils.getAntipatterns(systemName, antipattern)

	if antipattern == 'god_class':
		entities = dataUtils.getClasses(systemName)
	else:
		entities = []

	labels = []
	for entity in entities:
		if entity in true:
			labels.append([1, 0])
		else:
			labels.append([0, 1])

	return np.array(labels)

# Number of classes per system
systems_sizes = {
	'android-frameworks-opt-telephony': 190,
	'android-platform-support': 104,
	'apache-ant': 755,
	'apache-tomcat': 1005,
	'lucene': 160,
	'argouml': 1246,
	'jedit': 437,
	'xerces-2_7_0': 658
}

def getGodClassInstances(systemName):
	classes = dataUtils.getClasses(systemName)

	classToHistGCCM       = cm.getHistGCCM(systemName)
	classToDecorGCCM      = cm.getDecorGCCM(systemName)
	classToJDeodorantGCCM = cm.getJDeodorantGCCM(systemName)

	instances = []
	for klass in classes:
		instance = []
		instance.append(classToHistGCCM[klass])
		instance.append(classToDecorGCCM[klass])
		instance.append(classToJDeodorantGCCM[klass])

		instances.append(instance)

	instances = np.array(instances).astype(float)

	# Batch normalization
	scaler = StandardScaler()
	scaler.fit(instances)
	rescaledInstances = scaler.transform(instances)

	return rescaledInstances



