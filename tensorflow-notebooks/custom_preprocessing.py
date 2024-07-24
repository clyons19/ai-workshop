import tensorflow as tf

# Normalization
class StandardScaler: # Basic TensorFlow implementation of: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
	def __init__(self, copy=True, with_mean=True, with_std=True, axis=None):
		self.with_mean = with_mean
		self.with_std = with_std
		self.copy = copy
		self.axis = axis
	
	def _reset(self):
		if hasattr(self, "scale_"):
			del self.scale_
			del self.n_samples_seen_
			del self.mean_
			del self.var_

	def fit(self, data):
		self._reset()
		if not hasattr(self, "scale_"):
			if not isinstance(data, tf.Tensor):
				data = tf.constant(data, dtype='float32')
			self.mean_ = reduction_fnc_all_but_one_axis(tf.math.reduce_mean, data, self.axis, keepdims=True) if self.with_mean else create_reduced_filled_tensor(data, 0.0, self.axis)
			self.var_ = reduction_fnc_all_but_one_axis(tf.math.reduce_variance, data, self.axis, keepdims=True)+tf.constant(1e-8, dtype='float32') if self.with_std else create_reduced_filled_tensor(data, 1.0, self.axis)
			self.scale_ = tf.math.sqrt(self.var_)
			self.n_samples_seen_ = tf.size(data)

	def transform(self, data):
		if not hasattr(self, "scale_"):
			raise Exception("This StandardScaler has not be fitted yet.")
		if not isinstance(data, tf.Tensor):
			data = tf.constant(data, dtype='float32')
		return (data - self.mean_)/self.scale_
	
	def inverse_transform(self, data):
		if not hasattr(self, "scale_"):
			raise Exception("This StandardScaler has not be fitted yet.")
		if not isinstance(data, tf.Tensor):	
			data = tf.constant(data, dtype='float32')	
		return data*self.scale_ + self.mean_

# Standardization or unitization	
class MinMaxScaler: # Basic TensorFlow implementation of: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
	def __init__(self, feature_range=(0,1), copy=True, clip=False, axis=None):
		if feature_range[0] >= feature_range[1]:
			raise ValueError(
				"Minimum of desired feature range must be smaller than maximum. Got %s."
				% str(feature_range)
			)
		self.feature_range = feature_range
		self.copy = copy
		self.clip = clip
		self.axis = axis
	
	def _reset(self):
		if hasattr(self, "scale_"):
			del self.scale_
			del self.min_
			del self.n_samples_seen_
			del self.data_min_
			del self.data_max_
			del self.data_range_

	def fit(self, data):
		self._reset()
		if not hasattr(self, "scale_"):
			if not isinstance(data, tf.Tensor):
				data = tf.constant(data, dtype='float32')
			self.data_min_= reduction_fnc_all_but_one_axis(tf.math.reduce_min, data, self.axis, keepdims=True)
			self.data_max_ = reduction_fnc_all_but_one_axis(tf.math.reduce_max, data, self.axis, keepdims=True)
			self.data_range_ = self.data_max_ - self.data_min_
			self.scale_ = tf.constant((self.feature_range[1] - self.feature_range[0])/self.data_range_, dtype='float32')
			self.min_ = tf.constant(self.feature_range[0] - self.data_min_*self.scale_, dtype='float32')
			self.n_samples_seen_ = tf.size(data)

	def transform(self, data):
		if not hasattr(self, "scale_"):
			raise Exception("This MinMaxScaler has not be fitted yet.")
		if not isinstance(data, tf.Tensor):
			data = tf.constant(data, dtype='float32')
		return data*self.scale_ + self.min_
	
	def inverse_transform(self, data):
		if not hasattr(self, "scale_"):
			raise Exception("This MinMaxScaler has not be fitted yet.")	
		if not isinstance(data, tf.Tensor):
			data = tf.constant(data, dtype='float32')	
		return (data-self.min_)/self.scale_
	
def create_reduced_filled_tensor(x, value, axis_to_keep):
	"""
	Creates a value filled TensorFlow tensor with the same shape as the input tensor x,
	but with all but one selected axis reduced to 1.

	Parameters:
	x (tf.Tensor): The input tensor.
	value (float): Value to return in the filled tensor.
	axis_to_keep (int): The axis to keep the original size. None returns a constant.

	Returns:
	(tf.Tensor): The reduced value filled tensor.
	"""
	if axis_to_keep is None:
		return tf.constant(value, dtype=x.dtype)
	shape = tf.shape(x)
	if axis_to_keep < 0:
		axis_to_keep = len(shape) + axis_to_keep
	reduced_shape = tf.ones_like(shape)
	reduced_shape = tf.tensor_scatter_nd_update(reduced_shape, [[axis_to_keep]], [shape[axis_to_keep]]) # Set the dimension to keep to its original size
	reduced_zero_tensor = value*tf.ones(reduced_shape, dtype=x.dtype)
	return reduced_zero_tensor

def reduction_fnc_all_but_one_axis(op, tensor, axis_to_keep, keepdims=False):
	"""
	Applies reduction operation to a tensor across all but one specified axis.

	Parameters:
	op (tf.math.ReductionFunction): Reduction function to apply to tensor. One of [tf.math.reduce_XXX]
	tensor (tf.Tensor): The input tensor.
	axis_to_keep (int): The axis to keep. None reduces along all axes.

	Returns:
	reduced_tensor (tf.Tensor): The reduced tensor with mean computed across all but one axis.
	"""
	num_dims = len(tensor.shape)
	axes = list(range(num_dims))
	axes.pop(axis_to_keep)
	reduced_tensor = op(tensor, axis=axes, keepdims=keepdims)
	return reduced_tensor