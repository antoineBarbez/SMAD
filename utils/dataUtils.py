from __future__ import division
from context    import ROOT_DIR

import numpy as np

import csv
import entityUtils
import os
import progressbar

# Returns a list containing the history of the system.
# Granularity can be C or M for class or method history respectively.
def getHistory(systemName, granularity):
    assert granularity in ['M', 'C'], str(granularity) + " is not a valid granularity, choose C or M"
    
    if granularity == 'M':
        dirName = 'method_changes'
    
    if granularity == 'C':
        dirName = 'class_changes'

    # Create an history list containing the names of the entities 
    # (i.e, classes or methods) that changed in each commit.

    # For example, if entity1 and entity3 changed in the first commit, 
    # and entity1, entity2, entity3 changed in the second commit, etc ...
    # The history list will be [[entity1, entity3], [entity1, entity2, entity3], ...]

    historyFile = os.path.join(ROOT_DIR, 'data/history/' + dirName + '/' + systemName + '.csv')
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
    classFile = os.path.join(ROOT_DIR, 'data/entities/classes_all/' + systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            classes.append(row['Entity'])

    return classes

# Get only main classes in a system (name of the files).
def getClasses(systemName):
    classFile = os.path.join(ROOT_DIR, 'data/entities/classes/' + systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    return classes

# Get all the methods in a system
def getMethods(systemName):
    systemMethodsFile = os.path.join(ROOT_DIR, 'data/entities/methods/' + systemName + '.csv')

    methods = []
    with open(systemMethodsFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            methods.append(row[0])

    return methods

# Get the hand-validated occurences reported in the considered system for antipattern in [god_class, feature_envy].
def getAntipatterns(systemName, antipattern):
    assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose "god_class" or "feature_envy instead"'

    labelFile = os.path.join(ROOT_DIR, 'data/antipatterns/' + antipattern + '/' + systemName + '.txt')
    with open(labelFile, 'r') as file:
        return file.read().splitlines()

# A Feature Envy is a tuple (method, envied class) so the number of possible tuple for each system is nbMethod*nbClass.
# To reduce this number, we focus only on:
# - Non static, non accessor and non constructor methods.
# - Envied Class must be accessed (via method or attribute) at least one time in the body of the method.

# Returns the filtered Feature Envy candidates by looking at JDeodorant metric file (that implements the above conditions).
def getCandidateFeatureEnvy(systemName):
    JDMetricFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_metrics/' + systemName + '.csv')

    methods = getMethods(systemName)
    classes = getAllClasses(systemName)

    with open(JDMetricFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        return [entityUtils.normalizeMethodName(row['Method']) + ';' + row['TargetClass'] for row in reader \
            if (entityUtils.getEmbeddingClass(entityUtils.normalizeMethodName(row['Method']))!=row['TargetClass']) & (entityUtils.normalizeMethodName(row['Method']) in methods) & (row['TargetClass'] in classes)]  


### METRICS GETTERS FOR GOD CLASS ###

def getGCDecorMetrics(systemName):
    DecorBlobFile = os.path.join(ROOT_DIR, 'data/metric_files/decor/' + systemName + '.csv')

    classes = getClasses(systemName)

    dictionnary = {classes[i]: [0,0,0,0] for i in range(len(classes))}

    with open(DecorBlobFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        for row in reader:
            if row['ClassName'] in classes:
                nmdnad = float(row['NMD+NAD'])/float(row['nmdNadBound'])
                lcom = float(row['LCOM5'])/float(row['lcom5Bound'])
                cc = int(row['ControllerClass'])
                dataClass = int(row['nbDataClass'])

                dictionnary[row['ClassName']] = [nmdnad, lcom, cc, dataClass]


    return dictionnary


def getGCHistMetrics(systemName):
    # Get and prepare all data needed (classes, history)
    classes = getClasses(systemName)
    classToIndexMap = {klass: i for i, klass in enumerate(classes)}
    
    history = getHistory(systemName, "C")

    # Compute number of occurences for each class
    nbCommit = len(history)
    occurences = np.zeros(len(classes))
    for commit in history:
        for className in commit:
            if className in classes:
                idx = classToIndexMap[className]
                occurences[idx] = occurences[idx] + 1


    return {klass: [occurences[i]] for i, klass in enumerate(classes)}


def getGCJDeodorantMetrics(systemName):
    JDBlobFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/god_class_output/' + systemName + '.txt')

    classes = getClasses(systemName)

    dictionnary = {classes[i]: [0] for i in range(len(classes))}

    with open(JDBlobFile, 'r') as file:
        for line in file:
            className = line.split()[0]

            if className in classes:
               dictionnary[className][0] += 1
            
    return dictionnary




### METRICS GETTERS FOR FEATURE ENVY ###

def getFEHistMetrics(systemName):
    # Get and prepare all data needed (methods, classes, history)
    methods = getMethods(systemName)
    methodToIndexMap = {m: i for i, m in enumerate(methods)}
    
    classes = getAllClasses(systemName)
    classToIndexMap = {c: i for i, c in enumerate(classes)}

    history = getHistory(systemName, "M")

    # Initialize progressbar
    bar = progressbar.ProgressBar(maxval=len(history), \
        widgets=['Loading History for ' + systemName + ': ' ,progressbar.Percentage()])
    bar.start()


    # Number of commits in which the methods are involved
    occ = np.zeros(len(methods))

    # Matrix representing co-occurences between methods and classes, i.e, the number of time each 
    # methods of the system has been changed in commits involving methods of each class of the system.
    # For example, coOcc[i, j] = 5 means that the ith method of the system have been involved
    # 5 times in commits involving methods of the jth class of the system.
    coOcc = np.zeros((len(methods), len(classes)))
    
    for count, commit in enumerate(history):
        bar.update(count)
        for idx, method in enumerate(commit):
            if method in methods:
                # Get method Index 
                i = methodToIndexMap[method]

                # Increase nb of occurences the method
                occ[i] = occ[i] + 1

                # Get the other methods that changed together with the method in this commit
                coMethods = list(commit)
                del coMethods[idx]

                # Get the classes where these "other methods" are implemented
                klasses = []
                for m in coMethods:
                    embeddingClass = entityUtils.getEmbeddingClass(m)
                    if embeddingClass in classes:
                        klasses.append(embeddingClass)
                klasses = list(set(klasses))

                # For each of these classes increase the corresponding value in the occurences matrix
                for klass in klasses:
                    j = classToIndexMap[klass]
                    coOcc[i,j] = coOcc[i,j] + 1.
    bar.finish()

    for i, m in enumerate(methods):
        j = classToIndexMap[entityUtils.getEmbeddingClass(m)]
        
        if coOcc[i,j] == 0:
            coOcc[i,j] = 0.5
        
        coOcc[i,:] = coOcc[i,:]/coOcc[i,j]

    dictionnary= {}
    candidates = getCandidateFeatureEnvy(systemName)
    for entityName in candidates:
        method = entityName.split(';')[0]
        enviedClass = entityName.split(';')[1]
        i = methodToIndexMap[method]
        j = classToIndexMap[enviedClass]
        dictionnary[entityName] = [coOcc[i,j]]

    return dictionnary



def getFEInCodeMetrics(systemName):
    candidates = getCandidateFeatureEnvy(systemName)
    incodeMetricsFile = os.path.join(ROOT_DIR, 'data/metric_files/incode/' + systemName + '.csv')
    
    dictionnary = {candidate:[0.0, 0.0, 0.0] for candidate in candidates}
    currentMethodName = ''
    classAttributeMap = {}
    i = 0
    with open(incodeMetricsFile, 'rb') as csvfile:
        nbLines = len(csvfile.readlines()) - 2
        csvfile.seek(0)

        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            className = row['Class']
            methodName = className + '.' + row['Method']

            if (i == 0):
                currentMethodName = methodName
                currentClassName = className

            if (currentMethodName != methodName):
                classToMetricMap = getClassToMetricMap(currentClassName, classAttributeMap)
                normMethodName = entityUtils.normalizeMethodName(currentMethodName)
                for klass in classToMetricMap:
                    entityName = normMethodName + ';' + klass
                    if entityName in candidates:
                        dictionnary[entityName] = classToMetricMap[klass]


                classAttributeMap = {}
                classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])
                currentMethodName = methodName
                currentClassName = className
            else:
                classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])

            if (i == nbLines):
                currentMethodName = methodName
                currentClassName = className
                classAttributeMap[row['DeclaringClass']] = int(row['NbFields'])
                
                classToMetricMap = getClassToMetricMap(currentClassName, classAttributeMap)
                normMethodName = entityUtils.normalizeMethodName(currentMethodName)
                for klass in classToMetricMap:
                    entityName = normMethodName + ';' + klass
                    if entityName in candidates:
                        dictionnary[entityName] = classToMetricMap[klass]

            i = i + 1

    return dictionnary



def getClassToMetricMap(className, classAttributeMap):
    classToMetricMap = {}
    atfd = 3.0
    laa  = 3.0
    fdp  = 3.0

    FDP = len(classAttributeMap)

    # ATSD: Access To Self Data
    if className in classAttributeMap:
        ATSD = classAttributeMap[className]
        FDP = FDP - 1
    else:
        # To avoid division by zero
        ATSD = 0.5

    for klass in classAttributeMap:
        if klass != className:
            ATFD = int(classAttributeMap[klass])
            metric = (ATFD/atfd)*((ATFD/ATSD)/laa)*(fdp/FDP)
            classToMetricMap[klass] = [(ATFD/atfd), ((ATFD/ATSD)/laa), (FDP/fdp)]

    return classToMetricMap


def getFEJDeodorantMetrics(systemName):
    candidates = getCandidateFeatureEnvy(systemName)

    JDMetricFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_metrics/' + systemName + '.csv')

    dictionnary = {}
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
                        # Avoid division by zero
                        if nbAccessToEnclosingClass == 0.0:
                            nbAccessToEnclosingClass = 0.5

                        nbAccessMetric = tc['nbAccess'] / nbAccessToEnclosingClass
                        distanceMetric = tc['distance'] / distanceToEnclosingClass

                        dictionnary[entityName] = [nbAccessMetric, distanceMetric, 0.0]
                    
                
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
                        # Avoid division by zero
                        if nbAccessToEnclosingClass == 0.0:
                            nbAccessToEnclosingClass = 0.5

                        nbAccessMetric = tc['nbAccess'] / nbAccessToEnclosingClass
                        distanceMetric = tc['distance'] / distanceToEnclosingClass

                        dictionnary[entityName] = [nbAccessMetric, distanceMetric, 0.0]
                    
    JDOutputFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_output/' + systemName + '.txt')

    with open(JDOutputFile, 'r') as file:
        i = 0
        for line in file:
            if i > 0:
                method = line.split('\t')[1].replace('::', '.')
                method = method.split(':')[0]
                method = entityUtils.normalizeMethodName(method)
                targetClass = line.split('\t')[2]
                entityName = method + ';' + targetClass;

                if (entityName in dictionnary):
                    dictionnary[entityName][2] = 1.0
                    
            i = i + 1

    return dictionnary
