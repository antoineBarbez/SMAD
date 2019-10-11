from context import ROOT_DIR
from sklearn import tree

import approaches.asci.asci_utils as asci_utils
import utils.data_utils as data_utils
import utils.detection_utils as detection_utils
import numpy as np

import argparse
import os
import pickle

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'.")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the training will be performed using all the systems except this one.")
	parser.add_argument("-n_tree", type=int, default=10, help="The number of distinct trees to be trained and saved.")
	parser.add_argument("-min_samples_split", type=float)
	parser.add_argument("-max_features")
	parser.add_argument("-max_depth", type=int)
	parser.add_argument("-min_samples_leaf", type=int)
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	# Use the "optimal" hyper-parameters found via tuning if unspecified
	hyper_parameters = None
	for key in ['min_samples_split', 'max_features', 'max_depth', 'min_samples_leaf']:
		if args.__dict__[key] == None:
			if hyper_parameters == None:
				tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'asci', args.antipattern, args.test_system + '.csv')
				hyper_parameters = detection_utils.get_optimal_hyperparameters(tuning_file)
			args.__dict__[key] = hyper_parameters[' '.join(key.split('_')).capitalize()]

	# Remove the test system from the training set
	systems = data_utils.getSystems()
	systems.remove(args.test_system)
	systems = list(systems)

	# Get training instances
	x_train = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=0), [detection_utils.getInstances(args.antipattern, s) for s in systems])
	
	# Get ASCI training labels
	tools_predictions_list = [asci_utils.get_tools_predictions(args.antipattern, s) for s in systems]
	labels_list = [detection_utils.getLabels(args.antipattern, s) for s in systems]
	y_train_asci = asci_utils.get_asci_labels(tools_predictions_list, labels_list)

	# Get test data, note that here y_test contains the real labels while y_train_asci contains ASCI labels, i.e., tools' indexes
	x_test = detection_utils.getInstances(args.antipattern, args.test_system)
	y_test = detection_utils.getLabels(args.antipattern, args.test_system)
	tools_predictions_test = asci_utils.get_tools_predictions(args.antipattern, args.test_system)
	
	# Train and compute ensemble prediction on test set
	predictions = np.zeros((args.n_tree, x_test.shape[0], 1))
	for i in range(args.n_tree):
		clf = tree.DecisionTreeClassifier(
			min_samples_split=args.min_samples_split,
			max_features=args.max_features,
			max_depth=args.max_depth,
			min_samples_leaf=args.min_samples_leaf)
		clf = clf.fit(x_train, y_train_asci)

		# Save the tree
		with open(asci_utils.get_save_path(args.antipattern, args.test_system, i), 'wb') as save_file:
			pickle.dump(clf, save_file)

		# Compute the prediction of the current tree
		predicted_tool_indexes = clf.predict(x_test)
		for j, tool_index in enumerate(predicted_tool_indexes): 
			predictions[i, j, 0] = tools_predictions_test[tool_index][j]

	ensemble_prediction = np.mean(predictions, axis=0)

	# Print Ensemble performances
	print("\nPerformances on " + args.test_system + ": ")
	print('Precision: ' + str(detection_utils.precision(ensemble_prediction, y_test)))
	print('Recall   : ' + str(detection_utils.recall(ensemble_prediction, y_test)))
	print('MCC      : ' + str(detection_utils.mcc(ensemble_prediction, y_test)))