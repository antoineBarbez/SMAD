from context import ROOT_DIR

import numpy             as np
import tensorflow        as tf
import matplotlib.pyplot as plt

import os

# Returns the Bayesian averaging between many network's predictions
def ensemble_prediction(model, save_paths, input_x):
	saver = tf.train.Saver(max_to_keep=len(save_paths))
	predictions = []
	with tf.Session() as session:
		for save_path in save_paths:
			saver.restore(sess=session, save_path=save_path)
			prediction = session.run(model.inference, feed_dict={model.input_x: input_x})
			predictions.append(prediction)

	return np.mean(np.array(predictions), axis=0)

# Get the path of a trained model for a given approach (smad or asci)
def get_save_path(antipattern, test_system, model_number):
	directory = os.path.join(ROOT_DIR, 'approaches', 'smad', 'trained_models', antipattern, test_system)
	if not os.path.exists(directory):
			os.makedirs(directory)
	return os.path.join(directory, 'model_' + str(model_number))

# Plot learning curves with mean and standard deviations
# losses_train: a list of lists which contain losses values for training
# losses_test : same for testing
def plot_learning_curves(losses_train, losses_test):
	plt.figure()
	plt.ylim((0.0, 1.0))
	plt.xlabel("Epochs")
	plt.ylabel("Loss")
	mean_train = np.mean(losses_train, axis=0)
	mean_test = np.mean(losses_test, axis=0)
	percentile90_train = np.percentile(losses_train, 90, axis=0)
	percentile90_test  = np.percentile(losses_test, 90, axis=0)
	percentile10_train = np.percentile(losses_train, 10, axis=0)
	percentile10_test = np.percentile(losses_test, 10, axis=0)
	plt.grid()

	plt.fill_between(range(len(losses_train[0])), percentile90_train,
	                 percentile10_train, alpha=0.2,
	                 color="r")
	plt.fill_between(range(len(losses_test[0])), percentile90_test,
	                 percentile10_test, alpha=0.2,
	                 color="g")
	plt.plot(range(len(losses_train[0])), mean_train, color="r", label='Training set')
	plt.plot(range(len(losses_test[0])), mean_test, color="g", label='Test set')
	plt.legend(loc='best')
	plt.show()