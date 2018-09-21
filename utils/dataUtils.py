from __future__ import division
from context    import ROOT_DIR
#from   sklearn.preprocessing    import StandardScaler
#from   paths                    import ROOT_DIR

#import dataConstruction.systems as systems
import numpy                    as np

import csv
import os
import sys
import fnmatch
import pickle
import progressbar

''' This module is used to access data such as history, confidence metrics and instances'''

# Get a map containing the history of the system.
# granularity can be C or M for class or method history respectively.
def getHistory(systemName, granularity):
    if granularity == 'M':
        dirName = 'method_changes'
    elif granularity == 'C':
        dirName = 'class_changes'
    else:
        print(str(granularity) + " is not a valid granularity, choose C or M")
        return


    # Create an history list containing the names of the entities 
    # (i.e, classes or methods) that changed in each commit.

    # For example, if entity1 and entity3 changed in the first commit, 
    # and entity1, entity2, entity3 changed in the second commit, etc ...
    # The history list will be [[entity1, entity3], [entity1, entity2, entity3], ...]

    historyFile = ROOT_DIR + '/data/history/' + dirName + '/' + systemName + '.csv'
    with open(historyFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        rawHistory = [{key: row[key] for key in row} for row in reader]

        history  = []
        commit   = []
        snapshot = rawHistory[0]['Snapshot']
        for i, change in enumerate(rawHistory):
            if snapshot != change['Snapshot']:
                history.append(list(set(commit)))
                commit = []
                snapshot = change['Snapshot']

            commit.append(change['Entity'])
            
            if i == len(rawHistory)-1:
                history.append(list(set(commit)))

    return history


# Get the name of the classes in a system, except nested classes.  
def getAllClasses(systemName):
    classFile = ROOT_DIR + '/data/entities/classes_all/' + systemName + '.csv'

    classes = []
    with open(classFile, 'rb') as csvfile:
        rdr = csv.DictReader(csvfile, delimiter=';')
        for row in rdr:
            classes.append(row['Entity'])

    return classes

# Get only main classes in a system (name of the files).
def getClasses(systemName):
    classFile = ROOT_DIR + '/data/entities/classes/' + systemName + '.csv'

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    return classes

# Get all the methods in a system
def getMethods(systemName):
    systemMethodsFile = ROOT_DIR + '/data/entities/methods/' + systemName + '.csv'

    methods = []
    with open(systemMethodsFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            methods.append(row[0])

    return methods

# Get the hand-validated occurences reported in the considered system for antipattern in [god_class, feature_envy].
def getLabels(systemName, antipattern):
    if antipattern not in ['god_class', 'feature_envy']:
        print(str(antipattern) + ' not valid antipattern name. Choose "god_class" or "feature_envy instead"')
        return

    labelFile = os.path.join(ROOT_DIR, 'data/labels/' + antipattern + '/' + systemName + '.txt')
    with open(labelFile, 'r') as file:
        return file.read().splitlines()


#####     MERGED DETECTION INSTANCES GETTERS     #####
def getMDBlobInstances(systemName):
    classFile = os.path.join(ROOT_DIR, 'data/entities/classes/' + systemName + '.csv')

    JDDictionnary = getJDBlobMetrics(systemName)
    DecorDictionnary = getDecorBlobMetrics(systemName)
    HistDictionnary = getHistBlobMetrics(systemName)

    #Create Instances
    instances = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            className = row[0]

            instance = []
            instance.append(JDDictionnary[className])
            instance.append(DecorDictionnary[className])
            instance.append(HistDictionnary[className])
                           
            instances.append(instance)

    instances = np.array(instances).astype(float)
    
    # Batch normalization
    scaler = StandardScaler()
    scaler.fit(instances)
    rescaledInstances = scaler.transform(instances)

    # Compute system size + normalization
    sizes = []
    for system in (systems.systems_git + systems.systems_svn):
        count = 0
        with open(os.path.join(ROOT_DIR, 'data/entities/classes/' + system['name'] + '.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for className in reader:
                count = count + 1
        sizes.append(count)

    sizes = np.array(sizes).astype(float)
    scaler.fit(sizes.reshape(-1, 1))
    rescaledSize = scaler.transform(np.array([len(instances)]).astype(float).reshape(-1, 1))

    size = np.ones(len(instances)).reshape(-1, 1)*rescaledSize.reshape(-1)[0]


    return np.concatenate((rescaledInstances, size), axis=1)



# directory can be either 'generated' or 'hand_validated' depending on which system you want to get labels.
def getBlobLabels(systemName, directory):
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')
    blobFile = os.path.join(ROOT_DIR, 'data/labels/Blob/' + directory + '/' + systemName + '.csv')

    # Get Blobs of the system
    blobs = []
    with open(blobFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            blobs.append(row[0])

    # Make it in matrix form
    labels = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            className = row[0]

            if className in blobs:
                labels.append([1,0])
            else:
                labels.append([0,1])

    return np.array(labels)
    

