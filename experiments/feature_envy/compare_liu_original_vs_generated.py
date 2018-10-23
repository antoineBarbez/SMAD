from context import ROOT_DIR, nnUtils, dataUtils, entityUtils, liuUtils, liu_model

import tensorflow        as tf
import numpy             as np

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import model_from_json

import os
import math
import re

# Retrieve the version we trained on instances labeled by SMAD
def get_save_path_generated():
    return os.path.join(ROOT_DIR, 'neural_networks/liu_replication/trained_models/generated/network')

# Retrieve the "original" version trained on injected smells
def get_model_path_original(i):
    return os.path.join(ROOT_DIR, 'neural_networks/liu_replication/trained_models/injected/my_model_' + str(i) + '#Fold.json')

def get_model_weights_original(i):
    return os.path.join(ROOT_DIR, 'neural_networks/liu_replication/trained_models/injected/my_model_weights_' + str(i) + '#Fold.h5') 


# The next three methods are implemented to reproduce ROGOROUSLY the original
# implementation to test the model that can be found at:
# https://github.com/liuhuigmail/FeatureEnvy

def getWords(name):
    words = re.findall('[a-zA-Z][^A-Z]*', name)
    words = [word.lower() for word in words]

    if len(words) < 5:
        for _ in range(5-len(words)):
            words.insert(0, '*')
    if len(words) > 5:
        words = words[:5]

    return words

def getNames(entity):
    methodName = liuUtils.getMethodIdentifier(entity.split(';')[0])
    ownerClassName = entityUtils.getEmbeddingClass(entity.split(';')[0]).split('.')[-1]
    enviedClassName = entity.split(';')[-1].split('.')[-1]

    words = ''
    words += ' '.join(getWords(methodName))
    words += ' '
    words += ' '.join(getWords(ownerClassName))
    words += ' '
    words += ' '.join(getWords(enviedClassName))

    return words

def getInstances(systemName):
    entities = dataUtils.getCandidateFeatureEnvy(systemName)
    distanceMap = liuUtils.getDistanceMap(systemName)

    distances = []
    names = []
    for entity in entities:
        # Structural information
        distances.append(distanceMap[entity])

        # Lexical information
        names.append(getNames(entity))
        
    tokenizer = Tokenizer(num_words=None)
    tokenizer.fit_on_texts(names)
    test_sequences = tokenizer.texts_to_sequences(names)
    test_word_index = tokenizer.word_index
    test_data = pad_sequences(test_sequences, maxlen=15)  
    
    test_distances = np.asarray(distances)
    
    x_val = []
    x_val_names = test_data
    x_val_dis = test_distances
    x_val_dis = np.expand_dims(x_val_dis, axis=2)
    x_val.append(x_val_names)
    x_val.append(np.array(x_val_dis))

    return x_val

if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

    test_systems = ['apache-tomcat', 'jedit', 'android-platform-support']

    ### Test the model trained on instances labeled by SMAD ####
    tf.reset_default_graph()

    print('###  LIU_SMAD  ###')

    # Load data
    x_test_distances = []
    x_test_names = []
    y_test = []
    for system in test_systems:
        distances, names = liuUtils.getInstances(system)
        x_test_distances.append(distances)
        x_test_names.append(names)
        y_test.append(nnUtils.getLabels(system, 'feature_envy'))

    # Load the model
    model = liu_model.LiuCNN()
    saver = tf.train.Saver()
    session = tf.Session()
    saver.restore(sess=session, save_path=get_save_path_generated())

    # Compute performances
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

        if math.isnan(p):
            p = 0.0
        if math.isnan(r):
            r = 0.0
        if math.isnan(f):
            f = 0.0

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
    print('\n')


### Test the model trained on injected smells ###
    tf.reset_default_graph()
    print('###  LIU_INJ  ###')

    # cleanup
    del x_test_distances
    del x_test_names
    del y_test

    # Load data
    x_test = []
    y_test = []
    for system in test_systems:
        x_test.append(getInstances(system))
        y_test.append(nnUtils.getLabels(system, 'feature_envy'))

    # Load the model
    modelPath = get_model_path_original(4)
    modelWeights = get_model_weights_original(4)

    model = model_from_json(open(modelPath).read())  
    model.load_weights(modelWeights)

    session = tf.Session()

    # Compute performances
    preo = []
    reco = []
    f_mo = []
    for i in range(len(test_systems)):
        preds = model.predict_classes(x_test[i])
        
        detected = []
        for x in preds:
            if x[0] == 0:
                detected.append([0,1])
            else:
                detected.append([1,0])
        detected = np.array(detected) 

        p = nnUtils.precision(detected, y_test[i]).eval(session=session)
        r = nnUtils.recall(detected, y_test[i]).eval(session=session)
        f = nnUtils.f_measure(detected, y_test[i]).eval(session=session)

        print(test_systems[i])
        print('Precision: ' + str(p))
        print('Recall   : ' + str(r))
        print('F-measure: ' + str(f))
        print('')

        preo.append(p)
        reco.append(r)
        f_mo.append(f)

    session.close()

    print('')
    print('MEAN')
    print('Precision :' + str(np.mean(np.array(preo))))
    print('Recall    :' + str(np.mean(np.array(reco))))
    print('F-Mesure  :' + str(np.mean(np.array(f_mo))))
    print('')

