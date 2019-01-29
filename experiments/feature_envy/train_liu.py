from context import ROOT_DIR, nnUtils, dataUtils, entityUtils, liuUtils, liu_model

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import smad_fe
import os
import progressbar

# Train Liu's model on instances detected by SMAD

def get_save_path():
	return os.path.join(ROOT_DIR, 'neural_networks/liu_replication/trained_models/generated/network')

def generateLabels(systemName):
    entities = dataUtils.getCandidateFeatureEnvy(systemName)
    true = smad_fe.getSmells(systemName)

    labels = []
    for entity in entities:
        if entity in true:
            labels.append([1, 0])
        else:
            labels.append([0, 1])

    return np.array(labels)


if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

    training_systems = [
        'apache-derby',
        'apache-jena',
        'apache-log4j2',
        'apache-velocity',
        'javacc',
        'apache-jena',
        'jgraphx',
        'jgroups',
        'jhotdraw',
        'jspwiki',
        'mongodb',
        'pmd'
        ]
    
    test_systems = ['apache-tomcat', 'jedit', 'android-platform-support']

    # Get train and test data
    x_train_distances = []
    x_train_names = []
    y_train = []
    for system in training_systems:
        distances, names = liuUtils.getInstances(system)
        x_train_distances.append(distances)
        x_train_names.append(names)
        y_train.append(generateLabels(system))

    x_test_distances = []
    x_test_names = []
    y_test = []
    for system in test_systems:
        distances, names = liuUtils.getInstances(system)
        x_test_distances.append(distances)
        x_test_names.append(names)
        y_test.append(nnUtils.getLabels(system, 'feature_envy'))
		

	#constants
    num_steps     = 100
    learning_rate = 0.16201542516
    beta          = 0.00180316867055
    dropout       = 0.5


    model = liu_model.LiuCNN()
	saver = tf.train.Saver()
    session = tf.Session()

    # Initialize the variables of the TensorFlow graph.
    session.run(tf.global_variables_initializer())

    bar = progressbar.ProgressBar(maxval=num_steps, \
        widgets=['Training: ' ,progressbar.Percentage()])
    bar.start()


    losses_train = []
    losses_test  = []
    for step in range(num_steps):
        # Asymmetric training
        if (step<40):
            cut_names = 0.0
        else:
            cut_names = 1.0

        #Imballanced batch trainning
        l_train = []
        for i in range(len(y_train)):
            distances, names, labels = x_train_distances[i], x_train_names[i], y_train[i]
            feed_dict_train = {
                        model.input_distances: distances,
                        model.input_names: names,
                        model.input_y: labels,
                        model.learning_rate:learning_rate,
                        model.dropout_keep_prob: dropout,
                        model.beta: beta,
                        model.cut_names: cut_names}

            session.run(model.learning_step, feed_dict=feed_dict_train)

            l = session.run(model.loss, feed_dict=feed_dict_train)
            l_train.append(l)

        # Retieve test loss to plot learning curves
        l_test = []
        for i in range(len(y_test)):
            distances, names, labels = x_test_distances[i], x_test_names[i], y_test[i]
            feed_dict_test = {
                        model.input_distances: distances,
                        model.input_names: names,
                        model.input_y: labels,
                        model.dropout_keep_prob: 1.0,
                        model.cut_names: cut_names}

            l = session.run(model.loss, feed_dict=feed_dict_test)
            l_test.append(l)

        losses_train.append(np.mean(np.array(l_train)))
        losses_test.append(np.mean(np.array(l_test)))

        bar.update(step)
    bar.finish()

    # Save the optimized variables to disk.
	saver.save(sess=session, save_path=get_save_path())

    # Print performances
    pre = []
    rec = []
    f_m = []
    acc = []
    for i in range(len(y_test)):
        distances, names, labels = x_test_distances[i], x_test_names[i], y_test[i]
        feed_dict_test = {
                    model.input_distances: distances,
                    model.input_names: names,
                    model.dropout_keep_prob: 1.0,
                    model.cut_names:1.0}
        output = session.run(model.inference, feed_dict=feed_dict_test)
        p = nnUtils.precision(output, y_test[i]).eval(session=session)
        r = nnUtils.recall(output, y_test[i]).eval(session=session)
        f = nnUtils.f_measure(output, y_test[i]).eval(session=session)
        a = nnUtils.accuracy(output, y_test[i]).eval(session=session)

        print(test_systems[i])
        print('P :' + str(p))
        print('R :' + str(r))
        print('F :' + str(f))
        print('A :' + str(a))
        print('')

        pre.append(p)
        rec.append(r)
        f_m.append(f)
        acc.append(a)

    session.close()

	print('')
	print('MEAN')
	print('Precision :' + str(np.mean(np.array(pre))))
	print('Recall    :' + str(np.mean(np.array(rec))))
	print('F-Mesure  :' + str(np.mean(np.array(f_m))))
	print('Accuracy  :' + str(np.mean(np.array(acc))))
	print('')

	# Plot learning curves
	plt.plot(range(num_steps), losses_train, range(num_steps), losses_test)
	plt.show()


