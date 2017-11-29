from __future__ import print_function
from __future__ import division

import csv
import os
import sys
import fnmatch
import pickle

import numpy as np

''' This file contains all the methods that we will use to extract the data from
    the differents csv files (historical information, anti-pattern occurences...)'''

def readHistory(csvFile):
    with open(csvFile, 'rb') as csvfile:
        #print('start readind file :', csvFile)
        reader = csv.DictReader(csvfile, delimiter=';')
            changes = []
                for row in reader:
                    if row['Entity'] == 'METHOD':
                        code = row['Code'].split('.')
                            code.pop()
                                className = '.'.join(code)
                                
                                change = {}
                                change['Snapshot'] = row['Snapshot']
                                change['Class'] = className
                                changes.append(change)
                    
                        if row['Entity'] == 'CLASS':
                            change = {}
                                change['Snapshot'] = row['Snapshot']
                                change['Class'] = row['Code']
                                changes.append(change)
        
            return changes


#return the co-occurence matrix of the different classes
def getCoocMatrix(changes):
    print('start getting cooccurence matrix...')
        data = []
        classOcc = []
        commit = []
        commitNumber = changes[0]['Snapshot']
        for i, change in enumerate(changes):
            classOcc.append(change['Class'])
                if commitNumber != change['Snapshot']:
                    data.append(commit)
                        commit = []
                        commitNumber = change['Snapshot']
            
                commit.append(change['Class'])
                if i == len(changes)-1:
                    data.append(commit)
    
        classes = list(set(classOcc))
        size = len(classes)
        reverseDictionnary = {classes[i]: i for i in xrange(size)}
        
        coocMatrix = np.zeros((size,size), dtype=np.int16)
        
        print(len(data))
        i = 0
        #TODO this last part is very long at execution, try to reduce it !
        for commit in data:
            i = i + 1
                if(i % 100 ==0):
                    print(i)
            
                oneHotCommit = np.zeros((size,1), dtype=np.int16)
                for className in set(commit):
                    oneHotCommit[reverseDictionnary[className],0] = 1;
                
                        coocMatrix += oneHotCommit.dot(oneHotCommit.T)
        return reverseDictionnary , coocMatrix


#only use for test purpose
def getReverseDictionnary(csvFile):
    changes = readHistory(csvFile)
        
        data = []
        classOcc = []
        commit = []
        commitNumber = changes[0]['Snapshot']
        for i, change in enumerate(changes):
            classOcc.append(change['Class'])
                if commitNumber != change['Snapshot']:
                    data.append(commit)
                        commit = []
                        commitNumber = change['Snapshot']
            
                commit.append(change['Class'])
                if i == len(changes)-1:
                    data.append(commit)
    
        classes = list(set(classOcc))
        size = len(classes)
        reverseDictionnary = {classes[i]: i for i in xrange(size)}
        
    return reverseDictionnary


def saveCoocMatrices():
    for path,dirs,files in os.walk('./data/systems_history'):
        
        for f in fnmatch.filter(files,'*.csv'):
            historyFile = './data/systems_history/' + f
                fName = f.split('.')[0]
                    coocFile = './data/co-occurence_matrices/' + fName + '.pickle'
                        
                        changes = readHistory(historyFile)
                        reverseDictionnary , coocMatrix = getCoocMatrix(changes)
                        data = (reverseDictionnary , coocMatrix)
                        
                        with open(coocFile, 'wb') as file:
                            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

def saveCoocMatrices2():
    f = 'frameworks-base.csv'
        historyFile = './data/systems_history/' + f
        fName = f.split('.')[0]
        coocFile = './data/co-occurence_matrices/' + fName + '.pickle'
        
        changes = readHistory(historyFile)
        reverseDictionnary , coocMatrix = getCoocMatrix(changes)
        data = (reverseDictionnary , coocMatrix)
        
        with open(coocFile, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

def test():
    fileName = 'frameworks-tool-base.csv'
        #coocFile = './data/co-occurence_matrices/' + f
        historyFile = './data/systems_history/' + fileName
        blobOccurencesFile = './data/blob/' + fileName
        
        reverseDictionnary = getReverseDictionnary(historyFile)
        
        blobOccurences = np.zeros(len(reverseDictionnary))
        
        with open(blobOccurencesFile, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
                
                for row in reader:
                    blobOccurences[reverseDictionnary[row[0]]] = 1

#return the conditional probability matrix of the different classes
def getCPM(coocMatrix):
    '''concidering ci=True if the class i change in a commit ,
        CPM(i,j) = P(cj|ci) = coocMatrix(i,j)/coocMatrix(i,i)'''
            size = len(coocMatrix)
                eye = np.identity(size)
                    ones = np.ones(size).reshape(size,1)
                        
                        #DIV is a matrix which's column values are 1/coocMatrix(i,i)
                        DIV = ones.dot(np.divide(ones,(coocMatrix*eye).dot(ones)).T)
                            CPM = coocMatrix*DIV
                                
                                return CPM

''' return instances and labels that will be used to train some models later.
    The instances represents classes of a software
    and are of the form of a (nbClasses - 1 , 2) matrix where
    nbClasses is the number of classes in the given system.
    
    concidering I the instance corresponding to the ith class (ci) of a system,
    I(j,0) = P(ci | cj) and I(j, 1) = P(cj | ci)
    
    '''
def constructDataset():
    instances = []
        labels = np.array([])
        
        for path,dirs,files in os.walk('./data/co-occurence_matrices'):
            
            for f in fnmatch.filter(files,'*.pickle'):
                fileName = f.split('.')[0]
                    coocFile = './data/co-occurence_matrices/' + f
                        blobOccurencesFile = './data/blob/' + fileName + '.csv'
                        
                        with open(coocFile, 'r') as open_file:
                            reverseDictionnary , coocMatrix = pickle.load(open_file)
                                CPM = getCPM(coocMatrix)
                    
                        blobOccurences = np.zeros(len(reverseDictionnary))
                        
                        with open(blobOccurencesFile, 'rb') as csvfile:
                            reader = csv.reader(csvfile, delimiter=';')
                                
                                blobOccurences = np.zeros(len(reverseDictionnary))
                                for row in reader:
                                    blobOccurences[reverseDictionnary[row[0]]] = 1
                                
                                labels = np.append(labels, blobOccurences)
                        
                        for i in range(len(reverseDictionnary)):
                            c1 = CPM[:,i]
                                c2 = CPM[i,:]
                                c1 = np.delete(c1,i)
                                c2 = np.delete(c2,i)
                                
                                c = np.append(c1,c2).reshape(2,len(c1)).T
                                instances.append(c)

    return instances , labels


''' Same but here the instances are of the form of a vector [x1,x2,x3], where
    x1 = mean(P(ci|cj)) for P(ci|cj) != 0
    x2 = mean(P(cj|ci)) for P(cj|ci) != 0
    x3 = nb P != 0 / nb cj'''
def constructDataset2():
    instances = []
        labels = np.array([]).reshape(0,2)
        
        for path,dirs,files in os.walk('./data/co-occurence_matrices'):
            
            for f in fnmatch.filter(files,'*.pickle'):
                fileName = f.split('.')[0]
                    coocFile = './data/co-occurence_matrices/' + f
                        blobOccurencesFile = './data/blob/' + fileName + '.csv'
                        
                        with open(coocFile, 'r') as open_file:
                            reverseDictionnary , coocMatrix = pickle.load(open_file)
                                CPM = getCPM(coocMatrix)
                    
                        size = len(reverseDictionnary)
                        zeros = np.zeros(size)
                        ones = np.ones(size)
                        
                        with open(blobOccurencesFile, 'rb') as csvfile:
                            reader = csv.reader(csvfile, delimiter=';')
                                
                                for row in reader:
                                    zeros[reverseDictionnary[row[0]]] = 1
                                        ones[reverseDictionnary[row[0]]] = 0
                            
                                blobOccurences = np.append(zeros,ones).reshape(2,size).T
                                #print(blobOccurences.shape)
                                #print(blobOccurences)
                            labels = np.concatenate((labels, blobOccurences), axis=0)
        
        
        
                for i in range(len(reverseDictionnary)):
                    c1 = CPM[:,i]
                        c2 = CPM[i,:]
                            c1 = np.delete(c1,i)
                                c2 = np.delete(c2,i)
                                
                                idx = np.nonzero(c1)[0]
                                if idx.size != 0:
                                    x1 = np.mean([c1[i] for i in idx])
                                        x2 = np.mean([c2[i] for i in idx])
                                else:
                                    x1 = 0
                                        x2 = 0
                                x3 = idx.size/len(c1)
                                
                                x = [x1,x2,x3]
                            instances.append(x)


    return np.array(instances) , labels

def constructDataset3():
    instances = []
        labels = np.array([]).reshape(0,2)
        
        for path,dirs,files in os.walk('./data/co-occurence_matrices'):
            
            for f in fnmatch.filter(files,'*.pickle'):
                fileName = f.split('.')[0]
                    coocFile = './data/co-occurence_matrices/' + f
                        blobOccurencesFile = './data/blob/' + fileName + '.csv'
                        historyFile = './data/systems_history/' + fileName + '.csv'
                        
                        changes = readHistory(historyFile)
                        commits = []
                        for i, change in enumerate(changes):
                            commits.append(change['Snapshot'])
                        
                        print(len(set(commits)))
                        
                        with open(coocFile, 'r') as open_file:
                            reverseDictionnary , coocMatrix = pickle.load(open_file)
                                CPM = getCPM(coocMatrix)
                        
                        size = len(reverseDictionnary)
                        zeros = np.zeros(size)
                        ones = np.ones(size)
                        
                        with open(blobOccurencesFile, 'rb') as csvfile:
                            reader = csv.reader(csvfile, delimiter=';')
                                
                                for row in reader:
                                    zeros[reverseDictionnary[row[0]]] = 1
                                        ones[reverseDictionnary[row[0]]] = 0
                                
                                blobOccurences = np.append(zeros,ones).reshape(2,size).T
                                #print(blobOccurences.shape)
                                #print(blobOccurences)
                            labels = np.concatenate((labels, blobOccurences), axis=0)
                                
                                
                                
                                for i in range(len(reverseDictionnary)):
                                c1 = CPM[:,i]
                                c2 = CPM[i,:]
                                c1 = np.delete(c1,i)
                                c2 = np.delete(c2,i)
                                
                                idx = np.nonzero(c1)[0]
                                if idx.size != 0:
                                    x1 = np.mean([c1[i] for i in idx])
                                        x2 = np.mean([c2[i] for i in idx])
                                else:
                                    x1 = 0
                                        x2 = 0
                                x3 = idx.size/len(c1)
                                x4 = coocMatrix[i,i]/len(set(commits))
                                
                                
                                x = [x1,x2,x3,x4]
                                    instances.append(x)
    
    
    return np.array(instances) , labels

#used to test an idea, not important ....
def read(csvFile):
    with open(csvFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
            changes = []
                for row in reader:
                    if row['Entity'] == 'METHOD':
                        change = {}
                            change['Snapshot'] = row['Snapshot']
                                change['Methode'] = row['Code']
                                changes.append(change)
                
            return changes

def data2Text(csvFile):
    changes = read(csvFile)
        
        f = open('data.txt','a')
        
        commit = ''
        commitNumber = changes[0]['Snapshot']
        for change in changes:
            if commitNumber != change['Snapshot']:
                f.write(commit + '\n')
                    commit = ''
                        commitNumber = change['Snapshot']
                
            commit = commit + ' ' +change['Methode']
    
        f.close()


if __name__ == "__main__":
    '''changes = [
        {'Snapshot': '1', 'Class':'a'},
        {'Snapshot': '1', 'Class':'b'},
        {'Snapshot': '2', 'Class':'a'},
        {'Snapshot': '3', 'Class':'a'},
        {'Snapshot': '3', 'Class':'a'},
        {'Snapshot': '3', 'Class':'c'},
        {'Snapshot': '3', 'Class':'b'},
        {'Snapshot': '4', 'Class':'d'},
        {'Snapshot': '4', 'Class':'b'},
        {'Snapshot': '4', 'Class':'c'},
        {'Snapshot': '5', 'Class':'d'},
        {'Snapshot': '6', 'Class':'a'},
        {'Snapshot': '6', 'Class':'a'},
        {'Snapshot': '6', 'Class':'b'},
        {'Snapshot': '7', 'Class':'b'},
        {'Snapshot': '7', 'Class':'c'},
        ]
        
        reverseDictionnary , coocMatrix = getCoocMatrix(changes)
        print(reverseDictionnary)
        print(coocMatrix)
        data = (reverseDictionnary , coocMatrix)
        
        with open('./data/co-occurence_matrix/test.pickle', 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open('./data/co-occurence_matrix/test.pickle', 'r') as open_file:
        rd , cM = pickle.load(open_file)
        print(rd)
        print(cM)'''
            
            #x , y = constructDataset2()
            #print(x[1800])
            #print(y.shape)
            #print(y.sum())
            saveCoocMatrices2()

	


