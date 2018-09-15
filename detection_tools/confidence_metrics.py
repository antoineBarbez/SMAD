from context import ROOT_DIR, dataUtils

import csv
import os



###  GOD CLASS CONFIDENCE METRICS (GCCM)  ###

# DECOR
def computeDecorGCCM(nmdNad, nmdNadBound, lcom5, lcom5Bound, cc, nbDataClass):
    dataClass = min(int(nbDataClass), 3)
    nmdnad = min(float(nmdNad)/float(nmdNadBound), 6)
    lcom = min(float(lcom5)/float(lcom5Bound), 2)

    return (0.5 + dataClass) * (nmdnad + 0.5*(lcom + int(cc)))

# Returns a dictionary for which keys are the classes of the system, 
# and values are DECOR's confidence metrics for God Class detection.
def getDecorGCCM(systemName):
    DecorBlobFile = os.path.join(ROOT_DIR, 'detection_tools/metrics_files/god_class/Decor/' + systemName + '.csv')

    classes = dataUtils.getClasses(systemName)

    dictionnary = {classes[i]: 0 for i in range(len(classes))}

    with open(DecorBlobFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        for row in reader:
            if row['ClassName'] in classes:
                dictionnary[row['ClassName']] = computeDecorGCCM( row['NMD+NAD'],
                                                                row['nmdNadBound'], 
                                                                row['LCOM5'], 
                                                                row['lcom5Bound'], 
                                                                row['ControllerClass'], 
                                                                row['nbDataClass'])

    return dictionnary


def getJDeodorantGCCM(systemName):
    JDBlobFile = os.path.join(ROOT_DIR, 'detection_tools/metrics_files/god_class/JDeodorant/' + systemName + '.txt')

    classes = dataUtils.getClasses(systemName)

    dictionnary = {classes[i]: 0 for i in range(len(classes))}

    with open(JDBlobFile, 'r') as file:
        for line in file:
            className = line.split()[0]

            if className in classes:
               dictionnary[className] += 1
            
    return dictionnary


def getHistGCCM(systemName):
    classes = dataUtils.getClasses(systemName)
    classToIndexMap = {klass: i for i, klass in enumerate(classes)}
    
    # Create an history list containing the names of the classes that changed in each commit.
    # For example, if class1 and class3 changed in the first commit, 
    # and class1, class2, class3 changed in the second commit, etc ...
    # The history list will be [[class1, Class3], [class1, class2, class3], ...]

    history_dict = dataUtils.getHistory(systemName, "C")

    history = []
    commit = []
    snapshot = history_dict[0]['Snapshot']
    for i, change in enumerate(history_dict):
        if snapshot != change['Snapshot']:
            history.append(list(set(commit)))
            commit = []
            snapshot = change['Snapshot']

        commit.append(change['Entity'])
        
        if i == len(history_dict)-1:
            history.append(list(set(commit)))

    # Compute number of occurences for each class
    nbCommit = len(history)
    occurences = [0 for _ in classes]
    for commit in history:
        for className in commit:
            if className in classes:
                idx = classToIndexMap[className]
                occurences[idx] = occurences[idx] + 1


    return {klass: occurences[i] for i, klass in enumerate(classes)}

