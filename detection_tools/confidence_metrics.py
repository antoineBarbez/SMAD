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
    # Get and prepare all data needed (classes, history)
    classes = dataUtils.getClasses(systemName)
    classToIndexMap = {klass: i for i, klass in enumerate(classes)}
    
    history = dataUtils.getHistory(systemName, "C")

    # Compute number of occurences for each class
    nbCommit = len(history)
    occurences = [0 for _ in classes]
    for commit in history:
        for className in commit:
            if className in classes:
                idx = classToIndexMap[className]
                occurences[idx] = occurences[idx] + 1


    return {klass: occurences[i] for i, klass in enumerate(classes)}




###  FEATURE ENVY CONFIDENCE METRICS (FECM)  ###
# A Feature Envy is a tuple (method, envied class) so the number of possible tuple for each system is nbMethod*nbClass.
# To reduce this number, we focus only on the tuples that can potentially be detected by one of the three approaches.

# For Hist: if the method changes at least once with method(s) of a class
#def getRelevantMethodClass(systemName):


def getHistFECM(systemName):
    # Get and prepare all data needed (methods, classes, history)
    methods = dataUtils.getMethods(systemName)
    methodToIndexMap = {m: i for i, m in enumerate(methods)}
    
    classes = dataUtils.getAllClasses(systemName)
    classToIndexMap = {c: i for i, c in enumerate(classes)}

    history = dataUtils.getHistory(systemName, "M")

    # Initialize progressbar
    bar = progressbar.ProgressBar(maxval=len(history), \
        widgets=['Hist feature envy replication: ' ,progressbar.Percentage()])
    bar.start()


    # Number of commits in which the methods are involved
    occ = np.zeros(len(methods))

    # Matrix representing co-occurences between methods and classes, i.e, the number of time each 
    # methods of the system has been changed in commits involving methods of each class of the system.
    # For example, occurence[i, j] = 5 means that the ith method of the system have been involved
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

    ignore = []
    for i, m in enumerate(methods):
        if occ[i] == 0:
            ignore.append(m)

        j = classToIndexMap[entityUtils.getEmbeddingClass(m)]
        if coOcc[i,j] == 0:
            coOcc[i,j] = 0.5
        
        coOcc[i,:] = coOcc[i,:]/coOcc[i,j]

    FECM = {}
    for i, j in zip(*np.where(coOcc > 0)):
        if classes[j] != entityUtils.getEmbeddingClass(methods[i])
            instanceName = methods[i] + ';' + classes[j]
            FECM[instanceName] = coOcc[i,j]

        
    return FECM

def getInCodeFECM(systemName):
    incodeMetricsFile = os.path.join(ROOT_DIR, 'detection_tools/metrics_files/feature_envy/InCode/' + systemName + '.csv')

    methods = dataUtils.getMethods(systemName)
    classes = dataUtils.getAllClasses(systemName)

    
    FECM = {}
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
                    if (klass in classes) & (normMethodName in methods):
                        instanceName = normMethodName + ';' + klass
                        FECM[instanceName] = classToMetricMap[klass]


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
                    if (klass in classes) & (normMethodName in methods):
                        instanceName = normMethodName + ';' + klass
                        FECM[instanceName] = classToMetricMap[klass]

            i = i + 1


    return FECM



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
            classToMetricMap[klass] = metric

    return classToMetricMap


def getJDeodorantFECM(systemName):
    JDFEFile = ROOT_DIR + '/detection_tools/metrics_files/feature_envy/JDeodorant/' + systemName + '.txt'

    methods = dataUtils.getMethods(systemName)
    FECM = []
    with open(JDFEFile, 'r') as file:
        i = 0
        for line in file:
            if i > 0:
                source_entity = line.split('\t')[1].replace('::', '.')
                source_entity = source_entity.split(':')[0]
                source_entity = entityUtils.normalizeMethodName(source_entity)
                target_class = line.split('\t')[2]

                if source_entity in methods:
                    instanceName = source_entity + ';' + target_class
                    FECM[instanceName] = 1
            i = i + 1

    return list(set(smells))
