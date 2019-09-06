from context import ROOT_DIR, nnUtils, md

import tensorflow as tf
import numpy      as np

import argparse
import os
import progressbar
import random
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

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
	parser.add_argument("-n_step", type=int, default=100, help="Number of training steps (i.e., epochs) to be performed for each fold")
	parser.add_argument("-n_test", type=int, default=200, help="Number of random hyper-parameters sets to be tested")
	return parser.parse_args()

def generateRandomHyperParameters():
	learning_rate = 10**-random.uniform(0.0, 2.5)
	beta = 10**-random.uniform(0.0, 2.5)
	gamma = random.randint(1, 10)

	minBound = 4
	maxBound = 100
	dense_sizes = []
	nb_dense_layer = random.randint(1, 3)
	for _ in range(nb_dense_layer):
		dense_size = random.randint(minBound, maxBound)
		dense_sizes.append(dense_size)
		maxBound = dense_size

	return learning_rate, beta, gamma, dense_sizes

def train(session, model, x_train, y_train, num_step, lr, beta, gamma):
	for step in range(num_step):
		feed_dict_train = {
					model.input_x: x_train,
					model.input_y: y_train,
					model.learning_rate:lr,
					model.beta:beta,
					model.gamma:gamma}

		session.run(model.learning_step, feed_dict=feed_dict_train)

if __name__ == "__main__":
	args = parse_args()

	# Remove the test system from the set of systems
	systems.remove(args.test_system)

	bar = progressbar.ProgressBar(maxval=args.n_test, \
		widgets=['Performing cross validation for ' + args.test_system + ': ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results_2', 'smad', args.antipattern, args.test_system + '.csv')

	params = []
	perfs  = []
	for i in range(args.n_test):
		learning_rate, beta, gamma, dense_sizes = generateRandomHyperParameters()
		params.append([learning_rate, beta, gamma, dense_sizes])

		predictions = np.empty(shape=[0, 1])
		labels      = np.empty(shape=[0, 1])
		for validation_system in systems:
			x_train, y_train = nnUtils.build_dataset(args.antipattern, [s for s in systems if s != validation_system])
			x_valid, y_valid = nnUtils.build_dataset(args.antipattern, [validation_system])
			labels = np.concatenate((labels, y_valid), axis=0)

			# New graph
			tf.reset_default_graph()

			# Create model
			model = md.SMAD(
				shape=dense_sizes, 
				input_size=x_train.shape[-1])

			with tf.Session() as session:
				# Initialize the variables of the TensorFlow graph.
				session.run(tf.global_variables_initializer())

				# Train the model
				train(
					session=session,
					model=model,
					x_train=x_train,
					y_train=y_train,
					num_step=args.n_step,
					lr=learning_rate,
					beta=beta,
					gamma=gamma)

				predictions = np.concatenate((predictions, session.run(model.inference, feed_dict={model.input_x: x_valid})), axis=0)
		perfs.append(nnUtils.mcc(predictions, labels))

		indexes = np.argsort(np.array(perfs))
		with open(output_file_path, 'w') as file:
			file.write("Learning rate;Beta;Gamma;Dense sizes;MCC\n")
			for j in reversed(indexes):
				for k in range(len(params[j])):
					file.write(str(params[j][k]) + ';')
				file.write(str(perfs[j]) + '\n')
		bar.update(i+1)
	bar.finish()