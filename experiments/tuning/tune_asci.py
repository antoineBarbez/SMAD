from context import ROOT_DIR
from sklearn import tree

import approaches.asci.asci_utils as asci_utils
import utils.data_utils as data_utils
import utils.detection_utils as detection_utils
import numpy as np

import argparse
import os
import progressbar
import random

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'.")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the training will be performed using all the systems except this one.")
	parser.add_argument("-n_test", type=int, default=200, help="Number of random hyper-parameters sets to be tested")
	return parser.parse_args()

def generateRandomHyperparameters():
	max_features = random.choice(['sqrt', 'log2', None])
	max_depth = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None])
	min_samples_leaf = random.choice([1, 2, 3, 4, 5])
	min_samples_split = 10**-random.uniform(1.0, 4.0)

	return max_features, max_depth, min_samples_leaf, min_samples_split 

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the training set and build dataset
	systems = data_utils.getSystems()
	systems.remove(args.test_system)

	# Store instances, labels, and tools' predictions for each system (to reduce computation time)
	instances = {}
	labels    = {}
	tools_predictions = {}
	for system in systems:
		instances[system] = detection_utils.getInstances(args.antipattern, system)
		labels[system]    = detection_utils.getLabels(args.antipattern, system)
		tools_predictions[system] = asci_utils.get_tools_predictions(args.antipattern, system)

	# Initialize progress bar
	bar = progressbar.ProgressBar(maxval=args.n_test, \
		widgets=['Performing cross validation for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	# Get tuning file path
	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'asci', args.antipattern, args.test_system + '.csv')

	# Start tuning
	params = []
	perfs  = []
	for i in range(args.n_test):
		max_features, max_depth, min_samples_leaf, min_samples_split = generateRandomHyperparameters()
		params.append([max_features, max_depth, min_samples_leaf, min_samples_split])

		pred_overall   = np.empty(shape=[0, 1])
		labels_overall = np.empty(shape=[0, 1])
		for validation_system in systems:
			# Get instances and labels for the validation system
			x_valid = instances[validation_system]
			y_valid = labels[validation_system]

			training_systems = [s for s in systems if s != validation_system]
			
			# Get training instances
			x_train = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=0), [instances[s] for s in training_systems])
			
			# Get training ASCI labels
			tools_predictions_list = [tools_predictions[s] for s in training_systems]
			labels_list = [labels[s] for s in training_systems]
			y_train_asci = asci_utils.get_asci_labels(tools_predictions_list, labels_list)

			# Initialize decision tree
			clf = tree.DecisionTreeClassifier(
				max_features=max_features,
				max_depth=max_depth,
				min_samples_leaf=min_samples_leaf,
				min_samples_split=min_samples_split)

			# Train decision tree
			clf = clf.fit(x_train, y_train_asci)

			# Get predicted tool indexes
			pred_tool_indexes = clf.predict(x_valid)

			# Get predictions
			pred = np.zeros((len(y_valid), 1))
			for j, tool_index in enumerate(pred_tool_indexes): 
				pred[j, 0] = tools_predictions[validation_system][tool_index][j]

			# Store the predictions and labels
			pred_overall = np.concatenate((pred_overall, pred), axis=0)
			labels_overall = np.concatenate((labels_overall, y_valid), axis=0)
		
		# Compute overall performances
		perfs.append(detection_utils.mcc(pred_overall, labels_overall))
		
		# Update tuning file
		indexes = np.argsort(np.array(perfs))
		with open(output_file_path, 'w') as file:
			file.write("Max features;Max depth;Min samples leaf;Min samples split;MCC\n")
			for j in reversed(indexes):
				for k in range(len(params[j])):
					file.write(str(params[j][k]) + ';')
				file.write(str(perfs[j]) + '\n')
		bar.update(i+1)
	bar.finish()
