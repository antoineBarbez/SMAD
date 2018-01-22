from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import reader
import math

import transformData as td
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

learning_rate = 0.1
beta = 0.0
layers = [40,20,8]


num_labels = 2

def layer(x, input_size, output_size):
    w = tf.Variable(tf.truncated_normal(shape=[input_size, output_size]))
    b = tf.Variable(tf.zeros([output_size]))
    return w, tf.sigmoid(tf.matmul(x,w) + b)


graph = tf.Graph()
with graph.as_default():


    instances , labels = reader.constructDataset3()

    dataset_x , dataset_y = td.shuffle(instances , labels)

    '''data_x, data_y = shuffle.rebalanceData(2,dataset_x,dataset_y)

    validSet_start_idx = int(math.ceil(len(data_x)*0.7))

    x_train = data_x[:validSet_start_idx,:]
    y_train = data_y[:validSet_start_idx,:]
    x_valid = data_x[validSet_start_idx:,:]
    y_valid = data_y[validSet_start_idx:,:]'''

    validSet_start_idx = int(math.ceil(len(dataset_x)*0.7))

    train_data_x = dataset_x[:validSet_start_idx,:]
    train_data_y = dataset_y[:validSet_start_idx,:]
    x_valid = dataset_x[validSet_start_idx:,:]
    y_valid = dataset_y[validSet_start_idx:,:]

    #x_train, y_train = shuffle.rebalanceData(2, train_data_x, train_data_y)
    x_train, y_train = train_data_x, train_data_y

    # Input data. For the training data, we use a placeholder that will be fed
    # at run time with a training minibatch.
    x = tf.placeholder(tf.float32,[None,len(x_train[0])])
    y_ = tf.placeholder(tf.float32,[None,num_labels])


    h = x
    regularizers = 0
    input_size = len(x_train[0])
    for size in layers:
        w, h = layer(h, input_size, size)
        regularizers = regularizers + tf.nn.l2_loss(w)
        input_size = size

    weight = tf.Variable(tf.truncated_normal(shape=[input_size, num_labels]))
    biases = tf.Variable(tf.zeros([num_labels]))
    regularizers = regularizers + tf.nn.l2_loss(weight)
    logits = tf.matmul(h, weight) + biases 

    # Normal loss function
    #loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y_))
    # Loss function with L2 Regularization
    #loss = tf.reduce_mean(loss + beta * regularizers)


    param = tf.constant([1,0], tf.float32,shape=[1,2])
    A = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.multiply(y_,tf.nn.softmax(3*logits)),0,keep_dims=True),transpose_b=True))
    npos = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(y_,0,keep_dims=True),transpose_b=True))
    mpos = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.nn.softmax(3*logits),0,keep_dims=True),transpose_b=True))


    loss = 1 - 2*A/(npos+mpos)
    # Optimizer.
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

    # Predictions for the training
    train_prediction = tf.nn.softmax(logits)

    detected = tf.cast(tf.equal(tf.argmax(logits,1), 0), tf.float32)
    correct = tf.cast(tf.equal(tf.argmax(y_,1), 0), tf.float32)
    true_positive = tf.cast(tf.equal(tf.argmax(logits,1) + tf.argmax(y_,1), 0), tf.float32)

    precision = tf.reduce_sum(true_positive)/tf.reduce_sum(detected)
    recall = tf.reduce_sum(true_positive)/tf.reduce_sum(correct)
    f_mesure = 2*precision*recall/(precision+recall)

    #tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)), reduction_indices=[1]))
    T = tf.nn.softmax(logits)[0]
    #param = tf.constant([1,0], tf.float32,shape=[1,2])
    #TP = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.multiply(y_,tf.nn.softmax(3*logits)),0,keep_dims=True),transpose_b=True))
    #npos = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(y_,0,keep_dims=True),transpose_b=True))
    #mpos = tf.reduce_mean(tf.matmul(param, tf.reduce_sum(tf.nn.softmax(3*logits),0,keep_dims=True),transpose_b=True))
    TP2 = tf.reduce_sum(true_positive)
    TP3 = tf.reduce_sum(detected)



num_steps = 1000
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
        batch_data, batch_labels = td.shuffle(x_train, y_train)

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

    print(session.run([detected, correct, TP2,A,mpos,TP3], feed_dict={x: x_valid,
                                        y_: y_valid}))
    print(session.run([precision, recall, f_mesure], feed_dict={x: x_valid,
                                        y_: y_valid}))

    print('Best loss :',bestLoss,' at step :',bestLossStep)
    print('Best f-mesure :',bestFM,' at step :',bestFMStep)

    plt.plot(range(num_steps),losses,range(num_steps),fm)
    plt.show()