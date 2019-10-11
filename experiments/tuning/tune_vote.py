from context import ROOT_DIR

import approaches.asci.asci_utils as asci_utils
import utils.data_utils as data_utils
import utils.detection_utils as detection_utils
import numpy as np

import argparse
import os

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'.")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	nb_tools = 3
	k_values = [i+1 for i in range(nb_tools)]
	systems = data_utils.getSystems()

	# Get tools predictions and labels per system
	labels = {}
	tools_predictions = {}
	for system in systems:
		labels[system] = detection_utils.getLabels(args.antipattern, system)
		tools_predictions[system] = asci_utils.get_tools_predictions(args.antipattern, system)

	# Perform tuning for every system
	for test_system in systems:
		# Remove the test system from the tuning set
		tuning_systems = set(systems)
		tuning_systems.remove(test_system)

		# Get overall labels and overall tools predictions
		overall_labels = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=0), [labels[s] for s in tuning_systems])
		overall_tools_predictions = reduce(lambda x1, x2: np.concatenate((x1, x2), axis=1), [tools_predictions[s] for s in tuning_systems])

		# Start tuning	
		performances = []
		for k in k_values:
			overall_prediction = (np.sum(overall_tools_predictions, axis=0) >= k).astype(float)
			performances.append(detection_utils.mcc(overall_prediction, overall_labels))

		output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'vote', args.antipattern, test_system + '.csv')

		indexes = np.argsort(np.array(performances))
		with open(output_file_path, 'w') as file:
			file.write("Policy;MCC\n")
			for i in reversed(indexes):
				file.write("{0};{1}\n".format(i+1, performances[i]))
