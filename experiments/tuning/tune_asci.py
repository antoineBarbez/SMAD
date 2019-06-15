from context import ROOT_DIR, nnUtils, asci
from sklearn.model_selection import RandomizedSearchCV
from sklearn import tree

import numpy as np

import argparse
import os
import random

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
	parser.add_argument("-n_test", type=int, default=200, help="Number of random hyper-parameters sets to be tested")
	return parser.parse_args()

# Build the dataset for asci, i.e., the labels are the indexes of the best tool for each input instance.
# The order of the tools is given by the function asci.getToolsPredictions(...):
# idx = 0: DECOR, InCode
# idx = 1: HIST
# idx = 2: JDeodorant
def build_asci_dataset(antipattern, systems):
	# Get real instances and labels
	instances, labels = nnUtils.build_dataset(antipattern, systems, True)
	
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

	return instances, np.reshape(np.array(toolsIndexes), (len(toolsIndexes), 1))

def generateRandomHyperparameters():
	max_features = random.choice(['sqrt', 'log2', None])
	max_depth = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None])
	min_samples_leaf = random.choice([1, 2, 3, 4, 5])
	min_samples_split = 10**-random.uniform(1.0, 4.0)

	return max_features, max_depth, min_samples_leaf, min_samples_split 

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the training set and build dataset
	training_systems.remove(args.test_system)

	# Build ASCI training dataset: instances and asci labels (i.e., tools indexes)
	dataset_x, dataset_y = build_asci_dataset(args.antipattern, training_systems)

	params = []
	perfs  = np.zeros((args.n_test, 3))
	for i in range(args.n_test):
		max_features, max_depth, min_samples_leaf, min_samples_split = generateRandomHyperparameters()
		params.append([max_features, max_depth, min_samples_leaf, min_samples_split])
		
		# Due to the randomness of the process, repeat the cross validation 3 times 
		# per hyper-pameters' set and take the average performance value.
		for j in range(3):
			data_x, data_y = nnUtils.shuffle(dataset_x, dataset_y)
			predictions = np.empty(shape=[0, 1])
			for k in range(args.n_fold):
				# Create the training and testing datasets for this fold
				x_train, y_train, x_test, y_test = nnUtils.get_cross_validation_dataset(data_x, data_y, k, args.n_fold)

				clf = tree.DecisionTreeClassifier(
					max_features=max_features,
					max_depth=max_depth,
					min_samples_leaf=min_samples_leaf,
					min_samples_split=min_samples_split)

				clf = clf.fit(x_train, y_train)

				predictions = np.concatenate((predictions, np.reshape(clf.predict(x_test), (len(x_test), 1))), axis=0)
			perfs[i, j] = nnUtils.accuracy(predictions, data_y)

	perfs = np.mean(perfs, axis=1)
	indexes = np.argsort(perfs)

	tuning_results_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'asci', args.antipattern, args.test_system + '.csv')
	with open(tuning_results_file, 'w') as file:
		file.write("Max features;Max depth;Min samples leaf;Min samples split;Accuracy\n")
		for i in reversed(indexes):
			for j in range(len(params[i])):
				file.write(str(params[i][j]) + ';')
			file.write(str(perfs[i]) + '\n')
