from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import reader
import shuffle
import math

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

learning_rate = 0.05
num_nodes_1= 40
num_nodes_2 = 20
beta = 0.01

input_size = 5
num_labels = 2

graph = tf.Graph()
with graph.as_default():


    instances , labels = reader.constructDataset3()

    dataset_x , dataset_y = shuffle.shuffle(instances , labels)

    data_x, data_y = shuffle.rebalanceData(2,dataset_x,dataset_y)

    validSet_start_idx = int(math.ceil(len(data_x)*0.7))

    x_train = data_x[:validSet_start_idx,:]
    y_train = data_y[:validSet_start_idx,:]
    x_valid = data_x[validSet_start_idx:,:]
    y_valid = data_y[validSet_start_idx:,:]

    '''validSet_start_idx = int(math.ceil(len(dataset_x)*0.7))

    train_data_x = dataset_x[:validSet_start_idx,:]
    train_data_y = dataset_y[:validSet_start_idx,:]
    x_valid = dataset_x[validSet_start_idx:,:]
    y_valid = dataset_y[validSet_start_idx:,:]

    x_train, y_train = shuffle.rebalanceData(8, train_data_x, train_data_y)'''


    # Input data. For the training data, we use a placeholder that will be fed
    # at run time with a training minibatch.
    x = tf.placeholder(tf.float32,[None,input_size])
    y_ = tf.placeholder(tf.float32,[None,num_labels])

    # Variables.
    weights_1 = tf.Variable(tf.truncated_normal([input_size, num_nodes_1]))
    biases_1 = tf.Variable(tf.zeros([num_nodes_1]))
    weights_2 = tf.Variable(tf.truncated_normal([num_nodes_1, num_nodes_2]))
    biases_2 = tf.Variable(tf.zeros([num_nodes_2]))
    weights_3 = tf.Variable(tf.truncated_normal([num_nodes_2, num_labels]))
    biases_3 = tf.Variable(tf.zeros([num_labels]))

    # Training computation.
    logits_1 = tf.matmul(x, weights_1) + biases_1
    relu_layer_1= tf.nn.tanh(logits_1)
    logits_2 = tf.matmul(relu_layer_1, weights_2) + biases_2
    relu_layer_2= tf.nn.tanh(logits_2)
    logits_3 = tf.matmul(relu_layer_2, weights_3) + biases_3
    # Normal loss function
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits_3, labels=y_))
    # Loss function with L2 Regularization with beta=0.01
    regularizers = tf.nn.l2_loss(weights_1) + tf.nn.l2_loss(weights_2) + tf.nn.l2_loss(weights_3)
    loss = tf.reduce_mean(loss + beta * regularizers)

    # Optimizer.
    optimizer = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

    # Predictions for the training
    train_prediction = tf.nn.softmax(logits_3)

    detected = tf.cast(tf.equal(tf.argmax(logits_3,1), 0), tf.float32)
    correct = tf.cast(tf.equal(tf.argmax(y_,1), 0), tf.float32)
    true_positive = tf.cast(tf.equal(tf.argmax(logits_3,1) + tf.argmax(y_,1), 0), tf.float32)

    precision = tf.reduce_sum(true_positive)/tf.reduce_sum(detected)
    recall = tf.reduce_sum(true_positive)/tf.reduce_sum(correct)
    f_mesure = 2*precision*recall/(precision+recall)



num_steps = 4000
losses = []
fm = []
bestLossStep = 0
bestLoss = 100
bestFMStep = 0
bestFM = 0

with tf.Session(graph=graph) as session:
    session.run(tf.global_variables_initializer())
    print("Initialized")
    for step in range(num_steps):
        batch_data, batch_labels = shuffle.shuffle(x_train, y_train)

        feed_dict = {x: batch_data, y_: batch_labels}
        session.run(optimizer, feed_dict=feed_dict)
        l, f = session.run([loss, f_mesure], feed_dict={x:x_valid, y_:y_valid})
        losses.append(l)
        fm.append(f)

        if l < bestLoss:
            bestLoss = l
            bestLossStep = step

        if f > bestFM:
            bestFM = f
            bestFMStep = step


    print(session.run([precision, recall, f_mesure], feed_dict={x: x_valid,
                                        y_: y_valid}))

    print('Best loss :',bestLoss,' at step :',bestLossStep)
    print('Best f-mesure :',bestFM,' at step :',bestFMStep)

    plt.plot(range(num_steps),losses,range(num_steps),fm)
    plt.show()