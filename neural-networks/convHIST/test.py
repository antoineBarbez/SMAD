import tensorflow        as tf
import numpy             as np

import convHIST
import sys

sys.path.insert(0, '../')
from evaluateModel import *

sys.path.insert(0, '../../')
import reader

tf.reset_default_graph()


def get_save_path(net_number):
    save_dir = "./trained_models/final/"
    return save_dir + 'network' + str(net_number)


#Returns the averages predicted probabilities between all the neural networks
def ensemble_prediction(x):
    predictions = []
    for i in range(num_networks):
        # Reload the variables into the TensorFlow graph.
        saver.restore(sess=session, save_path=get_save_path(i))

        #Perform forward calculation
        feed_dict = {model.input_x: x, model.dropout_keep_prob:1.0}
        pred = session.run(model.inference, feed_dict=feed_dict)
        predictions.append(pred)

    return np.mean(np.array(predictions), axis=0)


test_systems = ['android-platform-support', 'apache-tomcat', 'jedit']

# Constants
num_networks = 1
filter_sizes = [3, 7, 17]
num_filters  = 20
fc_layers    = [100, 30]

# Create dataset
x_test = []
y_test = []
for systemName in test_systems:
    x = reader.getBlobInstances(systemName)
    y = reader.getBlobLabels(systemName, 'hand_validated')
    x_test.append(x)
    y_test.append(y)
    

# Create model
model = convHIST.convHist(filter_sizes, num_filters, fc_layers)

# To save and restore a trained model
saver = tf.train.Saver()

session = tf.Session()


# Evaluate the model on the test set
pre = []
rec = []
f_m = []
acc = []
for i in range(len(x_test)):
    output = ensemble_prediction(x_test[i])
    p = precision(output, y_test[i]).eval(session=session)
    r = recall(output, y_test[i]).eval(session=session)
    f = f_mesure(output, y_test[i]).eval(session=session)
    a = accuracy(output, y_test[i]).eval(session=session)

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




