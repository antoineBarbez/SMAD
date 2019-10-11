from context import ROOT_DIR

import utils.data_utils as data_utils
import utils.entity_utils as entity_utils

import csv
import os

def getGCCoreMetrics(systemName):
	JDMetricsFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'jdeodorant', 'god_class_output', systemName + '.txt')

	dictionnary = {c: [0] for c in data_utils.getClasses(systemName)}
	with open(JDMetricsFile, 'r') as file:
		for line in file:
			className = line.split()[0]

			if className in dictionnary:
				dictionnary[className][0] += 1

	return dictionnary


def getFECoreMetrics(systemName):
	JDMetricsFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'jdeodorant', 'feature_envy_metrics', systemName + '.csv')

	dictionnary = {e:[0., 0., 0.] for e in data_utils.getEntities('feature_envy', systemName)}
	with open(JDMetricsFile, 'rb') as metricfile:
		reader = csv.DictReader(metricfile, delimiter=';')
		data = [{key: row[key] for key in row} for row in reader]

		targetClasses = []
		nbAccessToEnclosingClass = 0.0
		distanceToEnclosingClass = 1.0
		method = data[0]['Method']
		for i, line in enumerate(data):
			if method != line['Method']:
				normMethodName = entity_utils.normalizeMethodName(method)
				for tc in targetClasses:
					entityName = normMethodName + ';' + tc['name']

					# Avoid division by zero
					if nbAccessToEnclosingClass == 0.0:
						nbAccessToEnclosingClass = 0.5

					nbAccessMetric = tc['nbAccess'] / nbAccessToEnclosingClass
					distanceMetric = tc['distance'] / distanceToEnclosingClass

					if entityName in dictionnary:
						dictionnary[entityName] = [nbAccessMetric, distanceMetric, 0.0]

				targetClasses = []
				nbAccessToEnclosingClass = 0.0
				distanceToEnclosingClass = 1.0
				method = line['Method']

			if entity_utils.getEmbeddingClass(entity_utils.normalizeMethodName(method)) == line['TargetClass']:
				nbAccessToEnclosingClass = float(line['NbAccessedEntities'])
				distanceToEnclosingClass = float(line['Distance_TC'])
			else:
				targetClasses.append({'name':line['TargetClass'], 'nbAccess':float(line['NbAccessedEntities']), 'distance':float(line['Distance_TC'])})

			if i == len(data)-1:
				normMethodName = entity_utils.normalizeMethodName(method)
				for tc in targetClasses:
					entityName = normMethodName + ';' + tc['name']

					# Avoid division by zero
					if nbAccessToEnclosingClass == 0.0:
						nbAccessToEnclosingClass = 0.5

					nbAccessMetric = tc['nbAccess'] / nbAccessToEnclosingClass
					distanceMetric = tc['distance'] / distanceToEnclosingClass

					if entityName in dictionnary:
						dictionnary[entityName] = [nbAccessMetric, distanceMetric, 0.0]
					
	JDOutputFile = os.path.join(ROOT_DIR, 'data', 'metric_files', 'jdeodorant', 'feature_envy_output', systemName + '.txt')
	with open(JDOutputFile, 'r') as file:
		i = 0
		for line in file:
			if i > 0:
				method = line.split('\t')[1].replace('::', '.')
				method = method.split(':')[0]
				method = entity_utils.normalizeMethodName(method)
				targetClass = line.split('\t')[2]
				entityName = method + ';' + targetClass;

				if entityName in dictionnary:
					dictionnary[entityName][2] = 1.0

			i +=1

	return dictionnary