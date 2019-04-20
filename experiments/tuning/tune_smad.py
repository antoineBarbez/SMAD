from context import ROOT_DIR, nnUtils, train_smad, md

import tensorflow        as tf
import numpy             as np

import argparse
import os
import progressbar
import random
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="Either 'god_class' or 'feature_envy'")
	parser.add_argument("test_system", help="The name of the system to be used for testing.\n Hence, the cross-validation will be performed using all the systems except this one.")
	parser.add_argument("-n_fold", type=int, default=5, help="Number of folds (k) for a k-fold-cross-validation")
	parser.add_argument("-n_step", type=int, default=100, help="Number of training steps (i.e., epochs) to be performed for each fold")
	parser.add_argument("-n_test", type=int, default=100, help="Number of random hyper-parameters sets to be tested")
	return parser.parse_args()

def generateRandomHyperParameters():
	learning_rate = 10**-random.uniform(0.0, 2.5)
	beta = 10**-random.uniform(0.0, 2.5)

	minBound = 4
	maxBound = 100
	dense_sizes = []
	nb_dense_layer = random.randint(1, 3)
	for _ in range(nb_dense_layer):
		dense_size = random.randint(minBound, maxBound)
		dense_sizes.append(dense_size)
		maxBound = dense_size

	return learning_rate, beta, dense_sizes

def get_cross_validation_dataset(X, Y, fold_index, n_fold):
	folds_x, folds_y = nnUtils.split(X, Y, n_fold)
	x_train = np.empty(shape=[0, X.shape[-1]])
	y_train = np.empty(shape=[0, 1])
	for i in range(n_fold):
		if i != fold_index:
			x_train = np.concatenate((x_train, folds_x[i]), axis=0)
			y_train = np.concatenate((y_train, folds_y[i]), axis=0)

	return x_train, y_train, folds_x[fold_index], folds_y[fold_index]

def train(session, model, x_train, y_train, num_step, lr, beta):
	for step in range(num_step):
		feed_dict_train = {
					model.input_x: x_train,
					model.input_y: y_train,
					model.learning_rate:lr,
					model.beta:beta}

		session.run(model.learning_step, feed_dict=feed_dict_train)

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the training set and build dataset
	train_smad.training_systems.remove(args.test_system)
	data_x, data_y = train_smad.build_dataset(args.antipattern, train_smad.training_systems)
	data_x, data_y = nnUtils.shuffle(data_x, data_y)

	bar = progressbar.ProgressBar(maxval=args.n_test, \
		widgets=['Performing cross validation for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'smad_' + args.antipattern + '_' + args.test_system + '.csv')

	params = []
	perfs  = []
	for i in range(args.n_test):
		learning_rate, beta, dense_sizes = generateRandomHyperParameters()
		params.append([learning_rate, beta, dense_sizes])

		predictions = np.empty(shape=[0, 1])
		for j in range(args.n_fold):
			x_train, y_train, x_test, y_test = get_cross_validation_dataset(data_x, data_y, j, args.n_fold)

			# New graph
			tf.reset_default_graph()

			# Create model
			model = md.SMAD(
				shape=dense_sizes, 
				input_size=x_train.shape[-1])

			with tf.Session() as session:
				# Initialize the variables of the TensorFlow graph.
				session.run(tf.global_variables_initializer())

				train(
					session=session,
					model=model,
					x_train=x_train,
					y_train=y_train,
					num_step=args.n_step,
					lr=learning_rate,
					beta=beta)

				predictions = np.concatenate((predictions, session.run(model.inference, feed_dict={model.input_x: x_test})), axis=0)
		
		perfs.append(nnUtils.f_measure(predictions, data_y))
		indexes = np.argsort(np.array(perfs))
		with open(output_file_path, 'w') as file:
			file.write("Learning rate;Beta;Dense sizes;F-measure\n")
			for j in reversed(indexes):
				for k in range(len(params[j])):
					file.write(str(params[j][k]) + ';')
				file.write(str(perfs[j]) + '\n')
		bar.update(i+1)
	bar.finish()