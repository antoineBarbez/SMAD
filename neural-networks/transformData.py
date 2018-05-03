import numpy             as np

import random


def shuffle(instances, labels):
	if len(instances) != len(labels):
		print('instances and labels must have the same number of elements')
		return

	idx = range(len(instances))
	random.shuffle(idx)

	x = np.array([instances[i] for i in idx])
	y = np.array([labels[i] for i in idx])
	
	return x, y
