from context import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import approaches.decor.core_metrics      as decor
import approaches.hist.core_metrics       as hist
import approaches.incode.core_metrics     as incode
import approaches.jdeodorant.core_metrics as jd
import numpy as np

import csv
import data_utils


### EVALUATION METRICS ###

def detected(output):
	return np.sum((output > 0.5).astype(float))

def positive(labels):
	return np.sum(labels)

def true_positive(output, labels):
	return np.sum((output + labels > 1.5).astype(float))

def precision(output, labels):
	return true_positive(output, labels)/detected(output)

def recall(output, labels):
	return true_positive(output, labels)/positive(labels)

def mcc(output, labels):
	'''
	Matthew's Correlation Coefficient
	'''
	N = labels.size
	N_pos = positive(labels)
	M_pos = detected(output)
	TP = true_positive(output, labels)

	return (TP*N - N_pos*M_pos)/(N_pos*M_pos*(N-N_pos)*(N-M_pos))**0.5


### INSTANCES AND LABELS GETTERS ###

def getLabels(antipattern, systemName):
	entities = data_utils.getEntities(antipattern, systemName)
	true = data_utils.getAntipatterns(antipattern, systemName)

	labels = np.zeros((len(entities), 1))
	for i, entity in enumerate(entities):
		if entity in true:
			labels[i, 0] = 1.

	return labels


def getInstances(antipattern, systemName, normalized=True):
	assert antipattern in ['god_class', 'feature_envy']

	metrics = []
	if antipattern == 'god_class':
		entities = data_utils.getClasses(systemName)
		metrics.append(decor.getGCCoreMetrics(systemName))
		metrics.append(hist.getGCCoreMetrics(systemName))
		metrics.append(jd.getGCCoreMetrics(systemName))
	else:
		entities = data_utils.getCandidateFeatureEnvy(systemName)
		metrics.append(incode.getFECoreMetrics(systemName))
		metrics.append(hist.getFECoreMetrics(systemName))
		metrics.append(jd.getFECoreMetrics(systemName))

	instances = []
	for entity in entities:
		instance = []
		for metricMap in metrics:
			instance += metricMap[entity]
		instances.append(instance)
	instances = np.array(instances).astype(float)

	# Normalization
	if normalized:
		scaler = StandardScaler()
		scaler.fit(instances)
		instances = scaler.transform(instances)

	return instances


### UTILS ###

def get_optimal_hyperparameters(tuning_file):
	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		hp = {}
		for row in reader:
			if row['MCC'] != 'nan':
				for key in row:
					try:
						hp[key] = eval(row[key])
					except NameError:
						hp[key] = row[key]
				break
		return hp

# Returns a set of antipatterns occurrences (entities names) given an array of predictions
def detectFromPredict(antipattern, systemName, prediction):
	entities = data_utils.getEntities(antipattern, systemName)

	return [entities[i] for i in range(len(entities)) if prediction[i]>0.5]

# Returns an array of predictions for each input instances from a set of smells
# i.e., the set of occurrences detected by an approach. 
def predictFromDetect(antipattern, systemName, smells):
	entities = data_utils.getEntities(antipattern, systemName)

	prediction = np.zeros((len(entities), 1))
	for i, entity in enumerate(entities):
		if entity in smells:
			prediction[i, 0] = 1.

	return prediction