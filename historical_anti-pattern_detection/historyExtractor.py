# -*- coding: utf-8 -*-
import subprocess
import os
import fnmatch
import urllib2
import json, ast
import progressbar
import re


''' Methods used to extract history information from the versionning systems of the differents sofwares,
	and extract the anti-pattern occurences from the landfill database (http://www.sesa.unisa.it/landﬁll/).
	all this data will be stored in csv files. '''

def getClassName(classPath, mainDirectory):
	className = classPath[len(mainDirectory):]
	className = className[:len(className)-len('.java')]
	className = '.'.join(className.split('/'))

	return className 

def getClassChange(SHA, date, filePath, changeType, mainDirectory):
	className = getClassName(filePath, mainDirectory)
	line = SHA + ';' + date + ';' + 'CLASS' + ';' + className + ';' + changeType + '\n'
	return line

def updateWorkingFile(wFilePath, filePath, SHA):
	F = open(wFilePath, "w")

	fileCommand = "git show " + SHA + ":" + filePath 
	ps = subprocess.Popen(fileCommand.split(), stdout=subprocess.PIPE)
	file, error = ps.communicate()

	F.write(file)
	F.close()

def getMethodsInFile(filePath):
	regex = '((public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\)\s*(\{))'

	methods = []
	with open(filePath, 'r') as javaFile:
		content = javaFile.read()
		m = re.findall(regex, content)
		for method in m:
			name = re.search('(\w+) *\([^\)]*\)', method[0]).groups()[0]
			params = re.search('\w+ *(\([^\)]*\))', method[0]).groups()[0]
			params = re.sub('\s+', ' ', params)
			
			methodName = name + params
			methods.append(methodName)

	return methods

def parseLine(line):
	match = re.search('\w+ *\([^\)]*\)', line)
	method = ""
	if match is not None:
		method = match.group(0)
	ct = None

	if re.search('method removed', line) is not None:
		ct = "REMOVED"

	if re.search('method added', line) is not None:
		ct = "ADDED"

	if re.search('code changed', line) is not None:
		ct = "BODY_MODIFIED"

	return method, ct

def getMethodeChange(SHA, date, filePath, changeType, mainDirectory):
	changes = []

	if changeType == "A":
		updateWorkingFile("../actualFile.java", filePath, SHA)
		methods = getMethodsInFile("../actualFile.java")

		for method in methods:
			change = method + ";" + "ADDED"
			changes.append(change)

	if changeType == "D":
		updateWorkingFile("../previousFile.java", filePath, SHA + "^")
		methods = getMethodsInFile("../previousFile.java")
		
		for method in methods:
			change = method + ";" + "DELETED"
			changes.append(change)

	if changeType == "M":
		updateWorkingFile("../actualFile.java", filePath, SHA)
		updateWorkingFile("../previousFile.java", filePath, SHA + "^")

		diffjCommand = "java -jar ../assets/frameworks/diffj-1.6.3.jar --brief ../previousFile.java ../actualFile.java"
		ps = subprocess.Popen(diffjCommand.split(), stdout=subprocess.PIPE)
		output, error = ps.communicate()

		diffs = output.split('\n')

		for line in diffs:
			method, ct = parseLine(line)

			if ct is not None:
				# store change like that, so it is hashable
				change = method + ";" + ct
				changes.append(change)


	lines = ""
	className = getClassName(filePath, mainDirectory)
	for change in set(changes):
		lines = lines + SHA + ';' + date + ';' + 'METHOD' + ';' + className + '.' + change + '\n'

	return lines

''' 
	creates the changes history file of the repository that is the cwd, 
	extract history information of files contained only in mainDirectory,
	set granularity to "C" to extract information at a file level granularity,
	set granularity to "M" to extract information at a methode level granularity.
'''

def createHistoryFile(mainDirectory, historyFilePath, granularity):
	F = open(historyFilePath, 'w')
	F.write('Snapshot;Date;Entity;Code;ChangeType\n')

	ps1 = subprocess.Popen(['git','log','--pretty=format:%H_%aD'], stdout=subprocess.PIPE)
	output1, error1 = ps1.communicate()

	commits = output1.split('\n')

	count = 0
	bar = progressbar.ProgressBar(maxval=len(commits), \
		widgets=['writing history file : ' ,progressbar.Percentage()])
	bar.start()

	options = {"C": getClassChange, "M": getMethodeChange}

	for line in commits:
		commit = line.split('_')
		SHA = commit[0]
		date = ' '.join(commit[1].split(' ')[1:4])
		
		count = count + 1
		bar.update(count)

		filesChangeCommand = "git diff-tree --no-commit-id --name-status -r " + SHA
		ps2 = subprocess.Popen(filesChangeCommand.split(), stdout=subprocess.PIPE)
		output2, error2 = ps2.communicate()

		for fileChange in output2.split('\n'):
			if fileChange.split('.')[-1] == 'java':
				if fileChange.split()[1].startswith(mainDirectory):
					changeType = fileChange.split()[0]
					filePath = fileChange.split()[1]

					change = options[granularity](SHA, date, filePath, changeType,mainDirectory)
					F.write(change)

	subprocess.call("rm -f ../previousFile.java", shell=True)
	subprocess.call("rm -f ../actualFile.java", shell=True)

	bar.finish()
	F.close()


#create a csv file containing all the classes/methods contained in the main directory
def createInstanceFile(mainDirectory, filePath, granularity):
	F = open(filePath, 'w')
	
	for path,dirs,files in os.walk('./' + mainDirectory):
		for f in fnmatch.filter(files,'*.java'):
			className = getClassName(os.path.join(path,f)[2:], mainDirectory)
			if granularity == "C":
				F.write(className + '\n')

			if granularity == "M":
				methods = getMethodsInFile(os.path.join(path,f))
				for method in methods:
					F.write(className + '.' + methodName + '\n')

	F.close()


def extractChangeHistory(repositoryURL, systemName, snapshot, mainDirectory, granularity = "C"):
	cloneCommand = 'git clone ' + repositoryURL + ' ' + systemName
	subprocess.call(cloneCommand, shell=True)

	cwd = os.getcwd()
	os.chdir(systemName)
	subprocess.call('git checkout -f '+ snapshot, shell=True)

	if granularity == "C":
		instanceFilePath = cwd + '/data/instances/classes/' + systemName + '.csv'
		historyFilePath = cwd + '/data/history/class_changes/' + systemName + '.csv'

	if granularity == "M":
		instanceFilePath = cwd + '/data/instances/methods/' + systemName + '.csv'
		historyFilePath = cwd + '/data/history/method_changes/' + systemName + '.csv'

	createInstanceFile(mainDirectory, instanceFilePath, granularity)
	createHistoryFile(mainDirectory, historyFilePath, granularity)

	subprocess.call('git checkout master', shell=True)
	os.chdir(cwd)

	removeDirCommand = "rm -rf " + systemName
	subprocess.call(removeDirCommand, shell=True)



if __name__ == "__main__":
	#extractChangeHistory('https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/', 'jedit', 'e343491b611efdd7a5313e7ba87d6a2d1d6f8804', '') #used git svn

	ptidejCommand = "java -jar ../assets/frameworks/PtidejSmellDetection.jar "

	