from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import reader
import shuffle
import math
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

FLAGS = None


def main(_):

  beta = 0.4

  instances , labels = reader.constructDataset2()

  dataset_x , dataset_y = shuffle.shuffle(instances , labels)

  data_x, data_y = shuffle.rebalanceData(2,dataset_x,dataset_y)

  validSet_start_idx = int(math.ceil(len(data_x)*0.7))

  x_train = data_x[:validSet_start_idx,:]
  y_train = data_y[:validSet_start_idx,:]
  x_valid = data_x[validSet_start_idx:,:]
  y_valid = data_y[validSet_start_idx:,:]

  '''
  validSet_start_idx = int(math.ceil(len(dataset_x)*0.7))

  train_data_x = dataset_x[:validSet_start_idx,:]
  train_data_y = dataset_y[:validSet_start_idx,:]
  x_valid = dataset_x[validSet_start_idx:,:]
  y_valid = dataset_y[validSet_start_idx:,:]

  x_train, y_train = shuffle.rebalanceData(3, train_data_x, train_data_y)'''

  # Create the model
  x = tf.placeholder(tf.float32, [None, 3])
  W = tf.Variable(tf.ones([3, 2]))
  b = tf.Variable(tf.ones([2]))
  y = tf.matmul(x, W) + b

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 2])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
  # outputs of 'y', and then average across the batch.
  #cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y) + 1e-10), reduction_indices=[1]))
  #ratio = 1
  #class_weight = [ratio, 1.0 - ratio]
  #weights = tf.constant([class_weight[int(i)] for i in y_train[:,0]])
  #logits = y # shape [batch_size, 2]
  #weighted_logits = tf.matmul(logits, class_weight) # shape [batch_size, 2]



  cross_entropy = tf.reduce_mean(
      tf.losses.softmax_cross_entropy(onehot_labels=y_, logits=y))
  
  regularizer = tf.nn.l2_loss(W)
  loss = tf.reduce_mean(cross_entropy + beta * regularizer)

  train_step = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

  #correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  #accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

  detected = tf.cast(tf.equal(tf.argmax(y,1), 0), tf.float32)
  correct = tf.cast(tf.equal(tf.argmax(y_,1), 0), tf.float32)
  true_positive = tf.cast(tf.equal(tf.argmax(y,1) + tf.argmax(y_,1), 0), tf.float32)

  precision = tf.reduce_sum(true_positive)/tf.reduce_sum(detected)
  recall = tf.reduce_sum(true_positive)/tf.reduce_sum(correct)
  f_mesure = 2*precision*recall/(precision+recall)

  numStep = 1000

  losses = []
  bestStep = 0
  bestLoss = 100

  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    # Train
    for step in range(numStep):
      #batch_xs, batch_ys = shuffle.shuffle(x_train, y_train)
      sess.run(train_step, feed_dict={x: x_train, y_: y_train})

      l = sess.run(cross_entropy, feed_dict={x:x_valid, y_:y_valid})
      losses.append(l)

      if l < bestLoss:
        bestLoss = l
        bestStep = step
    # Test trained model
    print(sess.run([precision, recall, f_mesure], feed_dict={x: x_valid,
                                        y_: y_valid}))

    #print(sess.run([tf.argmax(y,1), tf.argmax(y_,1)], feed_dict={x: x_valid,
    #                                    y_: y_valid}))

    print('Best loss :',bestLoss,' at step :',bestStep)
    plt.plot(range(numStep),losses)
    plt.show()

if __name__ == '__main__':
  tf.app.run(main=main)