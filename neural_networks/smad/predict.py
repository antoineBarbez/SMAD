from context import ROOT_DIR, nnUtils

import model      as md
import tensorflow as tf

import ast
import csv
import os

def predict(antipattern, system):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'smad', antipattern, system + '.csv')

	params = nnUtils.get_optimal_hyperparameters(tuning_file)
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