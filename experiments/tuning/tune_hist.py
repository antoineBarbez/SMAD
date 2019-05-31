from context import ROOT_DIR, nnUtils, hist_gc, hist_fe

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
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the cross-validation will be performed using all the systems except this one.")
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()

	# Remove the test system from the training set and build dataset
	systems.remove(args.test_system)
	systems = list(systems)

	# Get overall labels
	overall_labels = np.empty(shape=[0, 1])
	for system in systems:
		overall_labels = np.concatenate((overall_labels, nnUtils.getLabels(args.antipattern, system)), axis=0) 

	params = np.arange(0.0, 20.0, 0.5) if args.antipattern == 'god_class' else np.arange(1.0, 3.0, 0.1)
	hist_detect = hist_gc.detect_with_params if args.antipattern == 'god_class' else hist_fe.detect_with_params
	
	# Initialize progressbar
	bar = progressbar.ProgressBar(maxval=len(params), \
		widgets=['Tuning HIST parameters for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	perfs = []
	count = 0
	for alpha in params:
		count += 1
		bar.update(count)
		overall_prediction = np.empty(shape=[0, 1])
		for system in systems:
			prediction = nnUtils.predictFromDetect(args.antipattern, system, hist_detect(system, alpha))
			overall_prediction = np.concatenate((overall_prediction, prediction), axis=0)
		perfs.append(nnUtils.f_measure(overall_prediction, overall_labels))
	bar.finish()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'hist', args.antipattern, args.test_system + '.csv')

	indexes = np.argsort(np.array(perfs))
	with open(output_file_path, 'w') as file:
		file.write("Alpha;F-measure\n")
		for i in reversed(indexes):
			file.write(str(params[i]) + ';' + str(perfs[i]) + '\n')