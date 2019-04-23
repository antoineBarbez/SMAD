from context import ROOT_DIR, dataUtils, decor_gc, incode_fe, hist_gc, hist_fe, jdeodorant_gc, jdeodorant_fe

import numpy as np

def getOptimalPolicy(antipattern, test_system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'smad', antipattern, test_system + '.csv')

	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['F-measure'] != 'nan':
				return int(row['Policy'])

def getSmells(antipattern, system, k):
	assert antipattern in ['god_class', 'feature_envy']
	if antipattern == 'god_class':
		tools_outputs = [decor_gc.getSmells(system), hist_gc.getSmells(system), jdeodorant_gc.getSmells(system)]
	else:
		tools_outputs = [incode_fe.getSmells(system), hist_fe.getSmells(system), jdeodorant_fe.getSmells(system)]

	return vote(tools_outputs, k)

def predictWithPolicy(antipattern, system, k):
	entities = dataUtils.getEntities(antipattern, system)
	smells = getSmells(antipattern, system, k)

	prediction = []
	for entity in entities:
		if entity in smells:
			prediction.append([1.])
		else:
			prediction.append([0.])

	return np.array(prediction)

def predict(antipattern, system):
	k = getOptimalPolicy()
	return predictWithPolicy(antipattern, system, k)

# Outputs instances (i.e, class for God Class and method;enviedClass for Feature Envy) 
# detected using a vote over various tools outputs.
# tools_outputs: list containing the lists of instances detected by each tool
# k: mininum number of agreement to detect an instance
def vote(tools_outputs, k):
	assert k <= len(tools_outputs), "k can't be greater than the number of tools"

	# Map instances to the number of tools that have detected this instance
	instanceToNbToolMap = {}
	for toolOutput in tools_outputs:
		for instance in toolOutput:
			if instance in instanceToNbToolMap:
				instanceToNbToolMap[instance] = instanceToNbToolMap[instance] + 1
			else:
				instanceToNbToolMap[instance] = 1

	return [instance for instance in instanceToNbToolMap if instanceToNbToolMap[instance] >= k]