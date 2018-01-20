import tensorflow as tf
import sys
import math
import os
import numpy as np
import json
import pandas as pd

from keys import KEYS
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from tqdm import tqdm
from tensorflow.python.platform import gfile
from progress.bar import Bar

model_dir = 'Saved_models/'

def train_on(clothing_type, attributes, learning_rate, epochs, softmax=True):

	data_inputs = []
	data_labels = []

	if clothing_type == 'Tops':
		csv_file = 'CSVs/For training/clean_tops.csv'
	elif clothing_type == 'Bottoms':
		csv_file = 'CSVs/For training/clean_bottoms.csv'
	elif clothing_type == 'Shoes':
		csv_file = 'CSVs/For training/clean_shoes.csv'
	elif clothing_type == 'Denim':
		csv_file = 'CSVs/For training/clean_denims.csv'
	elif clothing_type == 'T-shirts':
		csv_file = 'CSVs/For training/clean_t-shirts.csv'
	elif clothing_type == 'Shirts':
		csv_file = 'CSVs/For training/clean_shirts.csv'

	### POPULATING DATA TO FEED INTO NEURAL NET
	csv_data = pd.read_csv(csv_file)

	for i in range(len(csv_data)):
		bottleneck_path = csv_data['bottleneck_dir'][i]
		bottleneck_file = open(bottleneck_path, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		data_inputs.append(bottleneck_values)

		label = csv_data.loc[i, KEYS[attributes]]
		data_labels.append(label)

	print (len(data_inputs))
	print (len(data_labels))
	
	# Splitting into train, val, and test
	train_inputs, valtest_inputs, train_labels, valtest_labels = train_test_split(data_inputs, data_labels, test_size=0.2, random_state=42)
	val_inputs, test_inputs, val_labels, test_labels = train_test_split(valtest_inputs, valtest_labels, test_size=0.4, random_state=43)

	# Setting hyperparameters. Learning rate and epochs is passed into function.
	batch_size = 128

	# useful info
	n_features = np.size(train_inputs, 1)
	n_labels = np.size(train_labels, 1)

	tf.reset_default_graph()
	graph = tf.get_default_graph()

	# Placeholders for input features and labels
	inputs = tf.placeholder(tf.float32, (None, n_features), name='inputs')
	labels = tf.placeholder(tf.float32, (None, n_labels), name='labels')

	# Setting up weights and bias
	weights = tf.Variable(tf.truncated_normal((n_features, n_labels), stddev=0.1), name='weights')
	bias = tf.Variable(tf.zeros(n_labels), name='bias')
	#tf.summary.histogram('weightshist', weights)
	#tf.summary.histogram('biashist', bias)

	if softmax:
		# Setting up operation in fully connected layer
		logits = tf.add(tf.matmul(inputs, weights), bias)
		prediction = tf.nn.softmax(logits, name='prediction')
		indices = tf.argmax(prediction, 1)

		# Defining loss of network
		difference = tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits)
		loss = tf.reduce_sum(difference)
		tf.summary.scalar('loss', loss)

		# Setting optimiser
		optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)

		# Define accuracy
		is_correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
		accuracy = tf.reduce_mean(tf.cast(is_correct_prediction, tf.float32))
		tf.summary.scalar('accuracy', accuracy)

	else:
		# Setting up operation in fully connected layer
		logits = tf.add(tf.matmul(inputs, weights), bias)
		prediction = tf.sigmoid(logits, name='prediction')
		pred = tf.round(prediction)

		# Defining loss of network
		difference = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits)
		loss = tf.reduce_sum(difference)
		tf.summary.scalar('loss', loss)

		# Setting optimiser
		optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)

		# Define accuracy
		is_correct_prediction = tf.equal(pred, labels)
		accuracy = tf.reduce_mean(tf.cast(is_correct_prediction, tf.float32))
		tf.summary.scalar('accuracy', accuracy)


	# For saving checkpoint after training
	saver = tf.train.Saver()

	merged = tf.summary.merge_all()

	# tensorboard --logdir=path/to/log  --> to view tensorboard

	# Run tensorflow session
	with tf.Session() as sess:
		init = tf.global_variables_initializer()
		sess.run(init)
		train_writer = tf.summary.FileWriter(model_dir+attributes, sess.graph)

		# Running the training in batches 
		batch_count = int(math.ceil(len(train_inputs)/batch_size))

		for epoch_i in range(epochs):
			batches_pbar = tqdm(range(batch_count), desc='Epoch {:>2}/{}'.format(epoch_i+1, epochs), unit='batches')
			# The training cycle
			for batch_i in batches_pbar:
				# Get a batch of training features and labels
				batch_start = batch_i*batch_size
				batch_inputs = train_inputs[batch_start:batch_start + batch_size]
				batch_labels = train_labels[batch_start:batch_start + batch_size]
				# Run optimizer
				_, summary = sess.run([optimizer, merged], feed_dict={inputs: batch_inputs, labels: batch_labels})
				train_writer.add_summary(summary, batch_i)

			# Check accuracy against validation data
			val_accuracy, val_loss = sess.run([accuracy, loss], feed_dict={inputs: val_inputs, labels: val_labels})
			print("After epoch {}, Loss: {}, Accuracy: {}".format(epoch_i+1, val_loss, val_accuracy))


		if softmax:
			test_accuracy, test_loss, indices = sess.run([accuracy, loss, indices], feed_dict={inputs: test_inputs, labels: test_labels})
			print ("TEST LOSS: {}, TEST ACCURACY: {}".format(test_loss, test_accuracy))

			true = np.argmax(test_labels, axis=1)

			# x-axis: predicted, y-axis: truth
			mat = confusion_matrix(true, indices)
			print ('Confusion matrix:')
			print (mat)

		else:
			test_accuracy, test_loss = sess.run([accuracy, loss], feed_dict={inputs: test_inputs, labels: test_labels})
			print ("TEST LOSS: {}, TEST ACCURACY: {}".format(test_loss, test_accuracy))

		g = tf.get_default_graph()
		result = saver.save(sess, model_dir+attributes+'/'+attributes)




if __name__ == '__main__':
	train_on('Shoes', 'Shoe_materials', 0.0005, 40, softmax=False)
	print (KEYS['Shoe_materials'])