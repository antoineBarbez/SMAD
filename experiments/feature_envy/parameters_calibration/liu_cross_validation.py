from context import ROOT_DIR, nnUtils, dataUtils, entityUtils, liuUtils, liu_model, smad

import tensorflow        as tf
import numpy             as np

import math
import os
import progressbar
import random

# Train and evaluate
def optimize(learning_rate, beta):
    # New graph
    tf.reset_default_graph()

    # Create model
    model = liu_model.LiuCNN()
    session = tf.Session()

    # Initialize the variables of the TensorFlow graph.
    session.run(tf.global_variables_initializer())

    for step in range(num_steps):
        #Imballanced batch trainning
        if step<40:
            cut_names = 0.0
        else:
            cut_names = 1.0
        
        for i in range(len(y_train)):
            distances, names, labels = x_train_distances[i], x_train_names[i], y_train[i]
            feed_dict_train = {
                    model.input_distances: distances,
                    model.input_names: names,
                    model.input_y: labels,
                    model.learning_rate: learning_rate,
                    model.beta: beta,
                    model.dropout_keep_prob: dropout,
                    model.cut_names: cut_names}

            session.run(model.learning_step, feed_dict=feed_dict_train)

    #Perform forward calculation
    results = []
    for i in range(len(x_test_distances)):
        feed_dict_test = {
                model.input_distances: x_test_distances[i],
                model.input_names: x_test_names[i],
                model.dropout_keep_prob: 1.0,
                model.cut_names: 1.0}

        output = session.run(model.inference, feed_dict=feed_dict_test)
        result = nnUtils.f_measure(output, y_test[i]).eval(session=session)
        
        if math.isnan(result):
                result = 0.0
        results.append(result)

    session.close()
    return np.mean(np.array(results))


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


def generateRandomHyperParameters():
    beta = 10**-random.uniform(0.0, 4.0)
    learning_rate = 10**-random.uniform(0.0, 4.0)

    return learning_rate, beta


if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

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
    
    test_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']

    #Constants
    num_tests      = 200
    num_steps      = 80
    num_networks   = 1

    dropout = 0.5

    # Instances and labels
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


    bar = progressbar.ProgressBar(maxval=num_tests, \
        widgets=['Performing cross validation: ' ,progressbar.Percentage()])
    bar.start()

    output_file_path = os.path.join(ROOT_DIR, 'experiments/feature_envy/parameters_calibration/outputs/liu_cv_results.csv')


    params = []
    perfs  = []
    for i in range(num_tests):
        learning_rate, beta = generateRandomHyperParameters()
        params.append([learning_rate, beta])
        f_measure = optimize(learning_rate, beta)
        perfs.append(f_measure)
        args = np.argsort(np.array(perfs))

        F = open(output_file_path, 'w')
        F.write("Learning rate;Beta;F-mesure\n")
        for k in reversed(args):
            F.write(str(params[k][0]) + ';' + str(params[k][1]) + ';' + str(perfs[k]) + '\n')
        F.close()
        bar.update(i+1)

    bar.finish()