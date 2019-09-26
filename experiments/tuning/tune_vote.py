from context import ROOT_DIR, nnUtils, vote

import numpy as np

import argparse
import math
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
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	k_values = [1, 2, 3]

	# Remove the test system from the training set
	training_systems.remove(args.test_system)

	performances = []
	for k in k_values:
		overall_prediction = np.empty(shape=[0, 1])
		overall_labels = np.empty(shape=[0, 1])
		for system in training_systems:
			prediction = nnUtils.predictFromDetect(args.antipattern, system, vote.detectWithPolicy(args.antipattern, system, k))
			labels = nnUtils.getLabels(args.antipattern, system)

			overall_prediction = np.concatenate((overall_prediction, prediction), axis=0)
			overall_labels = np.concatenate((overall_labels, labels), axis=0)

		performance = nnUtils.mcc(overall_prediction, overall_labels)
		if math.isnan(performance):
			performances.append(0.0)
		else:
			performances.append(performance)

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'vote', args.antipattern, args.test_system + '.csv')

	indexes = np.argsort(np.array(performances))
	with open(output_file_path, 'w') as file:
		file.write("Policy;MCC\n")
		for i in reversed(indexes):
			file.write(str(i+1) + ';')
			file.write(str(performances[i]) + '\n')
