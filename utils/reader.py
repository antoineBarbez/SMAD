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

    historyFile = ROOT_DIR + '/data/history/' + dirName + '/' + systemName + '.csv'
    with open(historyFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        changes = [{key: row[key] for key in row} for row in reader]

    return changes


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
        rdr = csv.reader(csvfile, delimiter=';')

        for row in rdr:
            methods.append(row[0])

    return methods


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


def computeClassHistoryTensor(systemName):
    historyFile = os.path.join(ROOT_DIR, 'data/history/class_changes/' + systemName + '.csv')
    classFile = os.path.join(ROOT_DIR, 'data/entities/classes/' + systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    reverseDictionnary = {classes[i]: i for i in range(len(classes))}

    history_dict = readHistory(historyFile, "C")

    history_list = []
    commit = []
    snapshot = history_dict[0]['Snapshot']
    for i, change in enumerate(history_dict):
        if snapshot != change['Snapshot']:
            history_list.append(list(set(commit)))
            commit = []
            snapshot = change['Snapshot']

        if change['Class'] in classes:
            commit.append(change['Class'])

        if i == len(history_dict)-1:
            history_list.append(list(set(commit)))

    history_tensor = []
    for commit in history_list:
        c = np.zeros(len(classes))
        for className in commit:
            i = reverseDictionnary[className]
            c[i] = 1
        history_tensor.append(c)
    history_tensor = np.array(history_tensor)

    return history_tensor


def computeBlobInstances(systemName):
    history_tensor = computeClassHistoryTensor(systemName)
    nbClass = history_tensor.shape[1]

    instances = []
    for i in range(nbClass):
        klass = history_tensor[:,i]
        mean = np.mean(np.delete(history_tensor, i, 1), 1)

        instances.append(np.stack((klass, mean), axis=-1))

    return instances



def getBlobInstances(systemName):
    instanceFile = os.path.join(ROOT_DIR, 'data/instances_tensors/classes/' + systemName + '.pickle')
    with open(instanceFile, 'r') as file:
        instances = pickle.load(file)

    return instances


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
    

# Used to save instances tensors that will be used to feed the CNN. To save time.
def saveTensors():
    stms = ['android-frameworks-opt-telephony',
            'android-platform-support',
            'apache-ant',
            'apache-derby',
            'apache-log4j1',
            'apache-log4j2',
            'apache-tomcat',
            'apache-velocity',
            'argouml',
            'javacc',
            'jedit',
            'jena',
            'jgraphx',
            'jgroups',
            'jhotdraw',
            'jspwiki',
            'junit',
            'lucene',
            'mongodb',
            'pmd',
            'xerces-2_7_0']

    for systemName in stms:
        print(systemName)
        tensorFile = os.path.join(ROOT_DIR, 'data/instances_tensors/classes/' + systemName + '.pickle')
        tensor = computeBlobInstances(systemName)

        with open(tensorFile, 'wb') as file:
            pickle.dump(tensor, file, protocol=pickle.HIGHEST_PROTOCOL)
    

