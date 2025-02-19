import os

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import sklearn

def train_and_test(model, train_data, test_data, val_data, learning_rate=0.001, batch_size=256, epochs=25):
	"""
	Trains and tests an image classification neural network model using a Mean Squared Error loss and Adam optimizer. Network outputs should be probability vectors of dimension matching One-Hot encoded classification labels.

	Inputs:
		model (tf.keras.Model): a TensorFlow image classification network. Network outputs should be probability vectors of dimension matching One-Hot encoded classification labels.
		train_data (tuple of arrays): network training data provided as a tuple of form (training_inputs, training_outputs)
		test_data (tuple of arrays): network testing data provided as a tuple of form (testing_inputs, testing_outputs)
		val_data (tuple of arrays): network validataion data provided as a tuple of form (validataion_inputs, validataion_outputs)
		learning_rate (float): learning rate for the network training. Default = 1e-3
		batch_size (int): batch size for the network training. Default = 256
		eepochs (int): number of training epochs. Default = 25

	Outputs:
		test errors (dict of floats): the testing loss and metrics return in a dictionary
	"""
	tf.random.set_seed(1)
	np.random.seed(1)

	train_x, train_y = train_data
	test_x, test_y = test_data

	loss_function = tf.keras.losses.MeanSquaredError()
	optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate) # the learning rate is essentially the gradient descent "step size"
	metrics = [
		'accuracy'
	] # metrics are provided as a list and each metric in the list will be evaluated

	model.compile(optimizer=optimizer, loss=loss_function, metrics=metrics) # compile the model by assigning it a loss function, optimizer, and (optionally) metrics

	_ = model(train_x[0:5]) # provide first 5 images as input
	model.summary()

	save_base = os.path.join('..', 'training-results')
	path_to_save = os.path.join(save_base, 'Trial 0')
	count = 0
	while os.path.exists(path_to_save):
		count += 1
		path_to_save = os.path.join(save_base, f'Trial {count}')
	os.makedirs(path_to_save)

	callbacks = [
		tf.keras.callbacks.ModelCheckpoint(os.path.join(path_to_save, 'best_weights.h5'), monitor='val_loss', save_best_only=True, save_weights_only=True) # Will watch the loss value on the validataion dataset and save the weights from the model that produces the best validataion loss
	]
	history = model.fit(train_x, train_y, batch_size=batch_size, epochs=epochs, validation_data=val_data, callbacks=callbacks) # train model. returns a History object containing the training and validataion losses and metrics

	# acc = history.history['accuracy']
	# val_acc = history.history['val_accuracy']

	# loss = history.history['loss']
	# val_loss = history.history['val_loss']

	# epochs_range = range(len(history.history['loss']))

	# plt.figure()
	# plt.subplot(1, 2, 1)
	# plt.plot(epochs_range, acc, label='Training Accuracy')
	# plt.plot(epochs_range, val_acc, label='Validation Accuracy')
	# plt.legend(loc='lower right')
	# plt.title('Training and Validation Accuracy')

	# plt.subplot(1, 2, 2)
	# plt.plot(epochs_range, loss, label='Training Loss')
	# plt.plot(epochs_range, val_loss, label='Validation Loss')
	# plt.legend(loc='upper right')
	# plt.title('Training and Validation Loss')
	# plt.tight_layout()
	# plt.show()

	print('Testing Results')
	test_errors = model.evaluate(test_x, test_y, batch_size=batch_size, return_dict=True)
	print(test_errors)

	return test_errors