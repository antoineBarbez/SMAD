from context import ROOT_DIR, nnUtils, asci
from sklearn.model_selection import RandomizedSearchCV
from sklearn import tree

import numpy as np

import argparse
import os

training_systems = {
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant',
	'lucene',
	'apache-tomcat',
	'argouml',
	'jedit',
	'xerces-2_7_0'
}

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'.")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the training will be performed using all the systems except this one.")
	parser.add_argument("-n_fold", type=int, default=5, help="Number of folds (k) for a k-fold-cross-validation")
	parser.add_argument("-n_test", type=int, default=100, help="Number of random hyper-parameters sets to be tested")
	return parser.parse_args()

# Build the dataset for asci, i.e., the labels are the indexes of the best tool for each input instance.
# The order of the tools is given by the function asci.getToolsPredictions(...):
# idx = 0: DECOR, InCode
# idx = 1: HIST
# idx = 2: JDeodorant
def build_asci_dataset(antipattern, systems):
	# Get real instances and labels
	instances, labels = nnUtils.build_dataset(antipattern, systems)
	
	# Compute the performances of each tool in order to sort them accordingly
	nb_tools = 3
	toolsOverallPredictions = [np.empty(shape=[0, 1]) for _ in range(nb_tools)]
	for system in systems:
		toolsPredictions = asci.getToolsPredictions(antipattern, system)
		for i in range(nb_tools):
			toolsOverallPredictions[i] = np.concatenate((toolsOverallPredictions[i], toolsPredictions[i]), axis=0)

	toolsPerformances = [nnUtils.f_measure(pred, labels) for pred in toolsOverallPredictions]

	# Indexes of the tools, sorted according to their performances on the training set
	toolsSortedIndexes = np.argsort(np.array(toolsPerformances))

	# Assign to each instance, the index of the tool that best predicted its label.
	# In case of conflict, assign the index of the tool that performed the best on overall.
	
	# Initialize with the index of the best tool as default index
	toolsIndexes = [toolsSortedIndexes[-1] for _ in instances]
	for i, label in enumerate(labels):
		for toolIndex in toolsSortedIndexes:
			if toolsOverallPredictions[toolIndex][i] == label:
				toolsIndexes[i] = toolIndex

	return instances, np.array(toolsIndexes)

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the training set and build dataset
	training_systems.remove(args.test_system)
	data_x, data_y = build_asci_dataset(args.antipattern, training_systems)

	random_grid = {
		'max_features': ['sqrt', 'log2', None],
		'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],
		'min_samples_leaf': [1, 2, 4, 6],
 		'min_samples_split': [2, 5, 10, 15]}

	cross_validation = RandomizedSearchCV(
		estimator = tree.DecisionTreeClassifier(),
		param_distributions = random_grid, 
		n_iter = args.n_test, 
		cv = args.n_fold,
		verbose=2, 
		n_jobs = -1)

	cross_validation.fit(data_x, data_y)
	best_params = cross_validation.best_params_

	tuning_results_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'asci', args.antipattern, args.test_system + '.csv')
	with open(tuning_results_file, 'w') as file:
		for key in best_params:
			file.write(str(key) + ';')
		file.write('\n')
		for key in best_params:
			file.write(str(best_params[key]) + ';')