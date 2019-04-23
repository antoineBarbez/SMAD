from context import ROOT_DIR, nnUtils

import model as md

import ast
import csv
import os

def get_optimal_parameters(antipattern, system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'smad', antipattern, test_system + '.csv')

	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['F-measure'] != 'nan':
				return {key:ast.literal_eval(row[key]) for key in row}

def predict(antipattern, system):
	params = get_optimal_parameters(antipattern, system)
	X = nnUtils.getInstances(antipattern, system)

	# New graph
	tf.reset_default_graph()

	# Create model
	model = md.SMAD(
		shape=params['Dense sizes'], 
		input_size=X.shape[-1])

	return nnUtils.ensemble_prediction(
		model=model,
		save_paths=[nnUtils.get_save_path('smad', antipattern, system, i) for i in range(10)], 
		input_x=X)