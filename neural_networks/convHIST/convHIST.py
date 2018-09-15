import tensorflow as tf

import sys

sys.path.insert(0, '../')
import fullyConnectedLayer
import customLoss


class convHist(object):
    def __init__(self, filter_sizes, num_filters, fc_layers, input_size=2):
        output_size = 2

        # Placeholders for instances and labels
        self.input_x = tf.placeholder(tf.float32, [None, None, input_size], name="input_x")
        self.input_y = tf.placeholder(tf.float32, [None, output_size], name="input_y")
        
        # Placeholders for learning parameters
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
        self.beta              = tf.placeholder(tf.float32, name="beta")
        
        self.input_expanded = tf.expand_dims(self.input_x, -1)

        # L2 loss
        L2_norm = tf.constant(0.0)

        # Create a convolution layers
        max_pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % filter_size):
                # Convolution Layer
                filter_shape = [filter_size, input_size, 1, num_filters]
                w = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="w")
                b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")
                conv = tf.nn.conv2d(
                    self.input_expanded,
                    w,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")
                
                # Apply nonlinearity
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                
                # 1-max pooling
                max_pooled = tf.reduce_max(
                    h,
                    axis=1,
                    keep_dims=True,
                    name="pool"
                )
                max_pooled_outputs.append(max_pooled)

        # Combine all the pooled features    
        num_filters_total = num_filters * len(filter_sizes)
            
        h_pool = tf.concat(max_pooled_outputs, 3)
        h_pool_flat = tf.reshape(h_pool, [-1, num_filters_total])

        # Add dropout
        with tf.name_scope("dropout"):
            h_drop = tf.nn.dropout(h_pool_flat, self.dropout_keep_prob)

            
        # Add fully connected layers
        h_in = h_drop
        n_in = num_filters_total
        for size in fc_layers:
            with tf.name_scope("full-%s" % size):
                layer = fullyConnectedLayer.Layer(h_in, n_in, size, 'xavier')
                h_in = layer.output
                n_in = size

                L2_norm += tf.nn.l2_loss(layer.w)
                L2_norm += tf.nn.l2_loss(layer.b)
        
        
        # Output layer
        with tf.name_scope("output"):
            outputLayer = fullyConnectedLayer.Layer(h_in, n_in, output_size, "xavier", tf.nn.softmax)
            L2_norm += tf.nn.l2_loss(outputLayer.w)
            L2_norm += tf.nn.l2_loss(outputLayer.b)

            # Forward calculation
            self.logits = tf.nn.xw_plus_b(outputLayer.input, outputLayer.w, outputLayer.b, name="logits")
            self.inference = outputLayer.output
        

        # Calculate custom loss
        with tf.name_scope("loss"):
            self.loss = customLoss.loss(self.logits, self.input_y) + self.beta * L2_norm

        # Learning mechanism
        self.learning_step = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)
        
