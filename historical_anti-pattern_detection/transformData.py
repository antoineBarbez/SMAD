from __future__            import division
from sklearn.preprocessing import StandardScaler

import numpy             as np
import matplotlib.pyplot as plt

import random
import reader

def shuffle(instances, labels):
	if len(instances) != len(labels):
		print('instances and labels must have the same number of elements')
		return

	idx = range(len(instances))
	random.shuffle(idx)

	x = np.array([instances[i] for i in idx])
	y = np.array([labels[i] for i in idx])
	
	return x, y

def rebalanceDataByRemovingInstances(instances, labels):

	class1Idx = np.nonzero(np.array(labels)[:,0])[0]
	class2Idx = np.nonzero(np.array(labels)[:,1])[0]

	ratio = class1Idx.size/class2Idx.size

	if ratio < 1:
		rate = int(1/ratio)
		class2Idx = class2Idx[::rate]
	else:
		rate = int(ratio)
		class1Idx = class1Idx[::rate]

	x = []
	y = []

	for i in class1Idx:
		x.append(instances[i])
		y.append([1,0])

	for i in class2Idx:
		x.append(instances[i])
		y.append([0,1])


	return shuffle(np.array(x), np.array(y))

def rebalanceData(constante, instances, labels):

	class1Idx = np.nonzero(labels[:,0])[0]
	class2Idx = np.nonzero(labels[:,1])[0]

	ratio = class1Idx.size/class2Idx.size

	if ratio < 1:
		minClass = class1Idx
		majClass = class2Idx
		onehotmin = [1,0]
		onehotmax = [0,1]
	else:
		minClass = class2Idx
		majClass = class1Idx
		onehotmin = [0,1]
		onehotmax = [1,0]
	
	if (ratio > constante or ratio > 1/constante):
		alpha = int(constante)
	else:
		alpha = int(max(ratio,1/ratio))

	minClassCopy = minClass
	for _ in range(alpha):
		minClass = np.append(minClass, minClassCopy)

	x = []
	y = []

	for i in minClass:
		x.append(instances[i])
		y.append(onehotmin)

	for i in majClass:
		x.append(instances[i])
		y.append(onehotmax)


	return rebalanceDataByRemovingInstances(x,y)

def standardizeData(data_x):
	scaler = StandardScaler(copy=False)
	scaler.scale_ = [0.31417215, 0.18947536, 0.27931839, 0.0159487]
	scaler.mean_ = [0.48356614, 0.38954064, 0.28556114, 0.00525554]
	scaler.var_ = [0.09870414, 0.03590091, 0.07801877, 0.00025436]

	rescaledX = scaler.transform(data_x)

	return rescaledX

def plotData(data_x, data_y):
	class1Idx = np.nonzero(data_y[:,0])[0]
	class2Idx = np.nonzero(data_y[:,1])[0]

	x1 = []
	y1 = []
	for i in class1Idx:
		x1.append(data_x[i,0])
		y1.append(data_x[i,1])

	x2 = []
	y2 = []

	for i in class2Idx:
		x2.append(data_x[i,0])
		y2.append(data_x[i,1])


	plt.plot(x1, y1, 'ro', x2, y2, 'bo')
	plt.show()



if __name__ == "__main__":
	'''
	instances  = [np.arange(6).reshape(3,2),np.zeros((3,2)),np.ones((3,2)),np.random.random((3,2))]
	labels = np.array([0,1,1,0])
	shuffle(instances,labels)
	'''

	'''
	instances , labels = reader.constructDataset2()
	scaler = StandardScaler().fit(instances)

	print(scaler.scale_)
	print(scaler.mean_)
	print(scaler.var_)
	'''


