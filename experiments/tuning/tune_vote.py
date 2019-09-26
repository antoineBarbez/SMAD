from context import ROOT_DIR, nnUtils, vote

import numpy as np

import argparse
import os

systems = [
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant',
	'lucene',
	'apache-tomcat',
	'argouml',
	'jedit',
	'xerces-2_7_0'
]

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'.")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	nb_tools = 3
	k_values = [i+1 for i in range(nb_tools)]

	# Get tools predictions and labels per system
	labels = {}
	tools_predictions = {}
	for system in systems:
		labels[system] = nnUtils.getLabels(args.antipattern, system)
		tools_predictions[system] = vote.getToolsPredictions(args.antipattern, system)

	# Perform tuning for every system
	for test_system in systems:
		# Remove the test system from the tuning set
		tuning_systems = set(systems)
		tuning_systems.remove(test_system)

		# Get overall labels and overall tools predictions
		overall_labels = np.empty(shape=[0, 1])
		overall_tools_predictions = np.empty(shape=[nb_tools, 0])
		for system in tuning_systems:
			overall_labels = np.concatenate((overall_labels, labels[system]), axis=0)
			overall_tools_predictions = np.concatenate((overall_tools_predictions, tools_predictions[system]), axis=1)

		# Start tuning	
		performances = []
		for k in k_values:
			overall_prediction = vote.vote(overall_tools_predictions, k)
			performances.append(nnUtils.mcc(overall_prediction, overall_labels))

		output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'vote', args.antipattern, test_system + '.csv')

		indexes = np.argsort(np.array(performances))
		with open(output_file_path, 'w') as file:
			file.write("Policy;MCC\n")
			for i in reversed(indexes):
				file.write(str(i+1) + ';')
				file.write(str(performances[i]) + '\n')
