from context import ROOT_DIR

import utils.data_utils as data_utils
import utils.detection_utils as detection_utils
import approaches.hist.core_metrics as hist_cm
import numpy as np

import argparse
import os
import progressbar

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the cross-validation will be performed using all the systems except this one.")
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()

	# Remove the test system from the training set and build dataset
	systems = data_utils.getSystems()
	systems.remove(args.test_system)
	systems = list(systems)

	# Get core-metrics
	core_metrics = {}
	for system in systems:
		if args.antipattern == 'god_class':
			core_metrics[system] = hist_cm.getGCCoreMetrics(system)
		else:
			core_metrics[system] = hist_cm.getFECoreMetrics(system)

	params = np.arange(0.0, 20.0, 0.5)/100. if args.antipattern == 'god_class' else np.arange(1.0, 4.0, 0.1)/100.

	# Initialize progressbar
	bar = progressbar.ProgressBar(maxval=len(params), \
		widgets=['Tuning HIST parameters for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	perfs = []
	for i, alpha in enumerate(params):
		bar.update(i)
		overall_prediction = np.empty(shape=[0, 1])
		overall_labels = np.empty(shape=[0, 1])
		for system in systems:
			smells = [entityName for entityName, ratio in core_metrics[system].items() if ratio[0]>alpha]
			prediction = detection_utils.predictFromDetect(args.antipattern, system, smells)
			overall_prediction = np.concatenate((overall_prediction, prediction), axis=0)
			overall_labels = np.concatenate((overall_labels, detection_utils.getLabels(args.antipattern, system)), axis=0)
		
		perfs.append(detection_utils.mcc(overall_prediction, overall_labels))
	bar.finish()
	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'hist', args.antipattern, args.test_system + '.csv')

	indexes = np.argsort(np.array(perfs))
	with open(output_file_path, 'w') as file:
		file.write("Alpha;MCC\n")
		for i in reversed(indexes):
			file.write("{0:.3f};{1}\n".format(params[i], perfs[i]))
