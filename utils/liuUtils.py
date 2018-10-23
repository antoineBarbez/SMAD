from context import ROOT_DIR

import tensorflow        as tf
import numpy             as np

import dataUtils
import entityUtils
import nnUtils

import csv
import re
import os

embeddings_index = {}
f = open(os.path.join(ROOT_DIR, 'neural_networks/liu_replication/word2vecNocopy.200d.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

MAX_SEQUENCE_LENGTH = 15 
EMBEDDING_DIM = 200

def getDistanceMap(systemName):
    candidates = dataUtils.getCandidateFeatureEnvy(systemName)

    JDMetricFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_metrics/' + systemName + '.csv')

    distanceMap = {}
    with open(JDMetricFile, 'rb') as metricfile:
        reader = csv.DictReader(metricfile, delimiter=';')
        data = [{key: row[key] for key in row} for row in reader]

        targetClasses = []
        nbAccessToEnclosingClass = 0.0
        distanceToEnclosingClass = 1.0
        method = data[0]['Method']
        for i, line in enumerate(data):
            if method != line['Method']:
                normMethodName = entityUtils.normalizeMethodName(method)
                for tc in targetClasses:
                    entityName = normMethodName + ';' + tc['name']
                    if entityName in candidates:
                        distanceMap[entityName] = [distanceToEnclosingClass, tc['distance']]


                targetClasses = []
                nbAccessToEnclosingClass = 0.0
                distanceToEnclosingClass = 1.0
                method = line['Method']

            if entityUtils.getEmbeddingClass(entityUtils.normalizeMethodName(method)) == line['TargetClass']:
                nbAccessToEnclosingClass = float(line['NbAccessedEntities'])
                distanceToEnclosingClass = float(line['Distance_TC'])
            else:
                targetClasses.append({'name':line['TargetClass'], 'nbAccess':float(line['NbAccessedEntities']), 'distance':float(line['Distance_TC'])})

            if i == len(data)-1:
                normMethodName = entityUtils.normalizeMethodName(method)
                for tc in targetClasses:
                    entityName = normMethodName + ';' + tc['name']
                    if entityName in candidates:
                        distanceMap[entityName] = [distanceToEnclosingClass, tc['distance']]

    return distanceMap

# Returns the identifier (i.e, the name) of a method from it's full name (classname.identifier(params)).
# The name should be normalized before using this method
def getMethodIdentifier(methodName):
    identifier = methodName.split('.')[-1]
    identifier = identifier.split('(')[0]

    return identifier

def getWords(name):
    words = re.findall('[a-zA-Z][^A-Z]*', name)
    words = [word.lower() for word in words]

    if len(words) > 5:
        words = words[:5]

    return words

def getEmbeddingMatrix(entity):
    methodName = getMethodIdentifier(entity.split(';')[0])
    ownerClassName = entityUtils.getEmbeddingClass(entity.split(';')[0]).split('.')[-1]
    enviedClassName = entity.split(';')[-1].split('.')[-1]

    words = []
    words += getWords(methodName)
    words += getWords(ownerClassName)
    words += getWords(enviedClassName)
    
    if len(words) < MAX_SEQUENCE_LENGTH:
        for _ in range(MAX_SEQUENCE_LENGTH - len(words)):
            words.insert(0, '*')

    assert len(words) == MAX_SEQUENCE_LENGTH
    
    embeddingMatrix = np.zeros((MAX_SEQUENCE_LENGTH, EMBEDDING_DIM))
    for i, word in enumerate(words):
        if word in embeddings_index:
            embeddingMatrix[i] = embeddings_index[word]

    return embeddingMatrix 

def getInstances(systemName):
    entities = dataUtils.getCandidateFeatureEnvy(systemName)
    distanceMap = getDistanceMap(systemName)

    distances = []
    names = []
    for entity in entities:
        # Structural information
        distances.append(distanceMap[entity])

        # Lexical information
        names.append(getEmbeddingMatrix(entity))
    return distances, names