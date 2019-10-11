from context import ROOT_DIR

import csv
import java_utils
import os

# Get the name of the classes in a system, except nested classes.  
def getAllClasses(systemName):
    classFile = os.path.join(ROOT_DIR, 'data','entities', 'classes_all', systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            classes.append(row['Entity'])

    return classes

# Get only main classes in a system (name of the files).
def getClasses(systemName):
    classFile = os.path.join(ROOT_DIR, 'data', 'entities', 'classes', systemName + '.csv')

    classes = []
    with open(classFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            classes.append(row[0])

    return classes

# Get all the methods in a system
def getMethods(systemName):
    systemMethodsFile = os.path.join(ROOT_DIR, 'data', 'entities', 'methods', systemName + '.csv')

    methods = []
    with open(systemMethodsFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            methods.append(row[0])

    return methods

# Get the hand-validated occurences reported in the considered system for antipattern in [god_class, feature_envy].
def getAntipatterns(antipattern, systemName):
    assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose "god_class" or "feature_envy instead"'

    labelFile = os.path.join(ROOT_DIR, 'data', 'antipatterns', antipattern, systemName + '.txt')
    with open(labelFile, 'r') as file:
        return file.read().splitlines()

# A Feature Envy is a tuple (method, envied class) so the number of possible tuple for each system is nbMethod*nbClass.
# To reduce this number, we focus only on:
# - Non static, non accessor and non constructor methods.
# - Envied Class must be accessed (via method or attribute) at least one time in the body of the method.

# Returns the filtered Feature Envy candidates by looking at JDeodorant metric file (that implements the above conditions).
def getCandidateFeatureEnvy(systemName):
    JDMetricFile = os.path.join(ROOT_DIR, 'approaches', 'jdeodorant', 'metric_files', 'feature_envy_metrics', systemName + '.csv')

    methods = getMethods(systemName)
    classes = getAllClasses(systemName)

    with open(JDMetricFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        return [java_utils.normalizeMethodName(row['Method']) + ';' + row['TargetClass'] for row in reader \
            if (java_utils.getEmbeddingClass(java_utils.normalizeMethodName(row['Method']))!=row['TargetClass']) & (java_utils.normalizeMethodName(row['Method']) in methods) & (row['TargetClass'] in classes)]  


def getEntities(antipattern, systemName):
    assert antipattern in ['god_class', 'feature_envy']

    if antipattern == 'god_class':
        return getClasses(systemName)
    else:
        return getCandidateFeatureEnvy(systemName)

def getSystems():
    systems = {
        'android-frameworks-opt-telephony',
        'android-platform-support',
        'apache-ant',
        'lucene',
        'apache-tomcat',
        'argouml',
        'jedit',
        'xerces-2_7_0'
    }

    return systems
