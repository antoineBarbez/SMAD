from context import ROOT_DIR, nnUtils, incode

import numpy as np

import argparse
import os
import progressbar

systems = {
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
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the training will be performed using all the systems except this one.")
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()

	# Remove the test system from the training set and build dataset
	systems.remove(args.test_system)
	systems = list(systems)

	# Get overall labels
	overall_labels = np.empty(shape=[0, 1])
	for system in systems:
		overall_labels = np.concatenate((overall_labels, nnUtils.getLabels('feature_envy', system)), axis=0) 

	params = [(atfd, laa, fdp) for atfd in range(1, 6) for laa in range(1, 6) for fdp in range(1, 6)]
	
	# Initialize progressbar
	bar = progressbar.ProgressBar(maxval=len(params), \
		widgets=['Tuning InCode parameters for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	perfs = []
	count = 0
	for atfd, laa, fdp in params:
		count += 1
		bar.update(count)
		overall_prediction = np.empty(shape=[0, 1])
		for system in systems:
			prediction = nnUtils.predictFromDetect('feature_envy', system, incode.detect_with_params(system, atfd, laa, fdp))
			overall_prediction = np.concatenate((overall_prediction, prediction), axis=0)
		perfs.append(nnUtils.mcc(overall_prediction, overall_labels))
	bar.finish()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'incode', args.test_system + '.csv')

	indexes = np.argsort(np.array(perfs))
	with open(output_file_path, 'w') as file:
		file.write("ATFD;LAA;FDP;MCC\n")
		for i in reversed(indexes):
			atfd, laa, fdp = params[i]
			file.write(str(atfd) + ';' + str(laa) + ';' + str(fdp) + ';')
			file.write(str(perfs[i]) + '\n')
