from __future__            import division
#from sklearn.preprocessing import StandardScaler
from paths                 import ROOT_DIR

import dataConstruction.systems as systems
import numpy as np

import csv
import os
import sys
import fnmatch
import pickle
import progressbar

import dataConstruction.repository_miner as rm 

''' This file contains all the methods that we will use to extract the data from 
    the differents csv files (historical information, anti-pattern occurences...)'''

def readHistory(csvFile, granularity):
    with open(csvFile, 'rb') as csvfile:
        #print('start readind file :', csvFile)
        reader = csv.DictReader(csvfile, delimiter=';')
        changes = []
        for row in reader:
            if granularity == 'M':
                change = {}
                change['Snapshot'] = row['Snapshot']
                #change['Class'] = row['Class']
                change['Method'] = row['Entity']
                change['ChangeType'] = row['ChangeType']
                changes.append(change)

            if granularity == 'C':
                change = {}
                change['Snapshot'] = row['Snapshot']
                change['Class'] = row['Code']
                changes.append(change)

        return changes


# Returns a dictionary for which keys are the classes of the system, 
# and values are JDeodorant's confidence metrics for Blob detection. 
def getJDBlobMetrics(systemName):
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')
    JDBlobFile = os.path.join(ROOT_DIR, 'advisors/results/JDeodorant/Blob/' + systemName + '.txt')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    dictionnary = {classes[i]: 0 for i in range(len(classes))}

    with open(JDBlobFile, 'r') as file:
        for line in file:
            className = line.split()[0]
            try:
               dictionnary[className] += 1
            except KeyError:
                pass

    return dictionnary

# Returns a dictionary for which keys are the classes of the system, 
# and values are DECOR's confidence metrics for Blob detection.
def getDecorBlobMetrics(systemName):
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')
    DecorBlobFile = os.path.join(ROOT_DIR, 'advisors/results/Decor/Blob/' + systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    dictionnary = {classes[i]: 0 for i in range(len(classes))}

    with open(DecorBlobFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        for row in reader:
            try:
                dictionnary[row['ClassName']] = computeDecorMetric( row['NMD+NAD'],
                                                                row['nmdNadBound'], 
                                                                row['LCOM5'], 
                                                                row['lcom5Bound'], 
                                                                row['ControllerClass'], 
                                                                row['nbDataClass'])
            except KeyError:
                pass

    return dictionnary


def computeDecorMetric(nmdNad, nmdNadBound, lcom5, lcom5Bound, cc, nbDataClass):
    dataClass = min(int(nbDataClass), 3)
    nmdnad = min(float(nmdNad)/float(nmdNadBound), 6)
    lcom = min(float(lcom5)/float(lcom5Bound), 2)

    return (0.5 + dataClass) * (nmdnad + 0.5*(lcom + int(cc)))


# Returns a dictionary for which keys are the classes of the system, 
# and values are HIST's confidence metrics for Blob detection.
def getHistBlobMetrics(systemName):
    historyFile = os.path.join(ROOT_DIR, 'data/history/class_changes/' + systemName + '.csv')
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')

    # Get the name of all the classes in the system's current version (the version used for the study)
    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    reverseDictionnary = {classes[i]: i for i in xrange(len(classes))}
    
    # Create an history list containing the names of the classes that changed in each commit.
    # For example, if class1 and class3 changed in the first commit, 
    # and class1, class2, class3 changed in the second commit, etc ...
    # The history list will be [[class1, Class3], [class1, class2, class3], ...]

    history_dict = readHistory(historyFile, "C")

    history = []
    commit = []
    snapshot = history_dict[0]['Snapshot']
    for i, change in enumerate(history_dict):
        if snapshot != change['Snapshot']:
            history.append(list(set(commit)))
            commit = []
            snapshot = change['Snapshot']

        commit.append(change['Class'])
        
        if i == len(history_dict)-1:
            history.append(list(set(commit)))

    # Compute number of occurences for each class
    nbCommit = len(history)
    occurences = [0 for _ in range(len(classes))]
    for commit in history:
        for className in commit:
            if className in classes:
                idx = reverseDictionnary[className]
                occurences[idx] = occurences[idx] + 1


    return {classes[i]: occurences[i] for i in range(len(classes))}



def getMDBlobInstances(systemName):
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')

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
        with open(os.path.join(ROOT_DIR, 'data/instances/classes/' + system['name'] + '.csv'), 'rb') as csvfile:
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
    classFile = os.path.join(ROOT_DIR, 'data/instances/classes/' + systemName + '.csv')

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


if __name__ == "__main__":
    rm.RepositoryMiner()
    

