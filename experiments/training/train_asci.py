from context import nnUtils, asci
from sklearn import tree

import numpy as np

import argparse
import pickle

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
	parser.add_argument("-n_tree", type=int, default=10, help="The number of distinct trees to be trained and saved.")
	parser.add_argument("-min_samples_split", type=float, default=0.01)
	parser.add_argument("-max_features", default=None)
	parser.add_argument("-max_depth", type=int, default=None)
	parser.add_argument("-min_samples_leaf", type=int, default=1)
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

	return instances, np.array(toolsIndexes)

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the training set and build dataset
	training_systems.remove(args.test_system)
	x_train, y_train = build_asci_dataset(args.antipattern, training_systems)
	
	# Test dataset, note that here y_test contains the real labels while y_train contains tools' indexes
	x_test, y_test = nnUtils.build_dataset(args.antipattern, [args.test_system], True)
	toolsPredictions = asci.getToolsPredictions(args.antipattern, args.test_system)
	
	# Train and compute ensemble prediction on test set
	predictions = np.zeros((args.n_tree, x_test.shape[0], 1))
	for i in range(args.n_tree):
		clf = tree.DecisionTreeClassifier(
			min_samples_split=args.min_samples_split,
			max_features=args.max_features,
			max_depth=args.max_depth,
			min_samples_leaf=args.min_samples_leaf)
		clf = clf.fit(x_train, y_train)

		# Save the tree
		with open(nnUtils.get_save_path('asci', args.antipattern, args.test_system, i), 'wb') as save_file:
			pickle.dump(clf, save_file)

		# Compute the prediction of the current tree
		predictedToolIndexes = clf.predict(x_test)
		for j, toolIndex in enumerate(predictedToolIndexes): 
			predictions[i, j, 0] = toolsPredictions[toolIndex][j]

	ensemble_prediction = np.mean(predictions, axis=0)

	# Print Ensemble performances
	print("\nPerformances on " + args.test_system + ": ")
	print('Precision: ' + str(nnUtils.precision(ensemble_prediction, y_test)))
	print('Recall   : ' + str(nnUtils.recall(ensemble_prediction, y_test)))
	print('F-Mesure : ' + str(nnUtils.f_measure(ensemble_prediction, y_test)))