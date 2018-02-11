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


#create a csv file containing all the classes contained in the main directory
def createClassesFile(mainDirectory, classesFilePath):
	F = open(classesFilePath, 'w')
	
	for path,dirs,files in os.walk('./' + mainDirectory):
		for f in fnmatch.filter(files,'*.java'):
			className = getClassName(os.path.join(path,f)[2:], mainDirectory)
			F.write(className + '\n')

	F.close()


def extractChangeHistory(repositoryURL, systemName, snapshot, mainDirectory, granularity = "C"):
	cloneCommand = 'git clone ' + repositoryURL + ' ' + systemName
	subprocess.call(cloneCommand, shell=True)

	cwd = os.getcwd()
	os.chdir(systemName)
	subprocess.call('git checkout -f '+ snapshot, shell=True)

	classFile = cwd + '/data/systems_methods/' + systemName + '.csv'
	historyFile = cwd + '/data/systems_history/' + systemName + '.csv'
	#createClassesFile(mainDirectory, classFile)
	createHistoryFile(mainDirectory, historyFile, granularity)

	subprocess.call('git checkout master', shell=True)
	os.chdir(cwd)

	removeDirCommand = "rm -rf " + systemName
	subprocess.call(removeDirCommand, shell=True)



if __name__ == "__main__":
	#extractSmellOccurences()
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'apache-ant', 'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 'src/main/')
	#extractChangeHistory('https://android.googlesource.com/platform/frameworks/support', 'android-platform-support', '38fc0cf9d7e38258009f1a053d35827e24563de6', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/cassandra.git', 'apache-cassandra', '4f9e551', '')
	#extractChangeHistory('https://github.com/apache/commons-codec.git', 'apache-commons-codec', 'c6c8ae7a', '')
	#extractChangeHistory('https://github.com/apache/commons-io.git', 'apache-commons-io', '99c5008d71b61f84a114038b064d58c837ee7ed6', '')
	#extractChangeHistory('https://github.com/apache/commons-lang.git', 'apache-commons-lang', 'f957d81625a3aa70385f50d87f036ebe2c54613f', '')
	#extractChangeHistory('https://github.com/apache/commons-logging.git', 'apache-commons-logging', 'd821ed3e', '')
	#extractChangeHistory('https://github.com/apache/derby.git', 'apache-derby', '562a9252', '')
	#extractChangeHistory('https://github.com/apache/tomcat.git', 'apache-tomcat', '398ca7ee', '')
	#extractChangeHistory('https://github.com/eclipse/eclipse.jdt.core.git', 'eclipse-jdt-core', '0eb04df7', 'org.eclipse.jdt.core/model/')
	#extractChangeHistory('https://github.com/google/guava.git', 'google-guava', 'e8959ed0', '') #YES
	#extractChangeHistory('https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/', 'jedit', 'ffb4fb679e305e9e74fd9134a8965838c982825d', '') #used git svn
	#extractChangeHistory('https://github.com/mongodb/mongo-java-driver.git', 'mongodb', 'b67c0c43', '')
	#extractChangeHistory('https://android.googlesource.com/platform/frameworks/opt/telephony', 'android-frameworks-opt-telephony', 'c241cad754ecf27c96b09f1e585b8be341dfcb71', '')
	#extractChangeHistory('https://android.googlesource.com/platform/tools/base', 'android-frameworks-tool-base', 'c03df13c68e4470f71da54732db3aee5051f706c', '') #YES
	#extractChangeHistory('https://android.googlesource.com/platform/frameworks/base', 'android-frameworks-base', '9066cfe9886ac131c34d59ed0e2d287b0e3c0087', '')
	#extractChangeHistory('https://android.googlesource.com/platform/sdk', 'android-frameworks-sdk', '04b07a76650a6ffd719c55f593b21fb1d92c84d2', '')
	#extractChangeHistory('https://github.com/apache/ant-ivy', 'apache-ivy', 'eb93c4dc62e24ecf0778539782a3d90a9a712e01', '')
	#extractChangeHistory('https://github.com/apache/karaf.git', 'apache-karaf', 'cf84f16070327f9ee0b310977ff2d6a454ae20bb', '')
	#extractChangeHistory('https://github.com/apache/log4j.git', 'apache-log4j', '7cf64b6c9692e596193a0b11e38367721cf1c938', '')
	#extractChangeHistory('https://github.com/apache/pig.git', 'apache-pig', 'a8c680cf28ad4c2ab824c268a3dbe2783667dd94', '')
	#extractChangeHistory('https://github.com/apache/struts.git', 'apache-struts', '9ad9404bfac2b936e1b5f0f5e828335bc5a51b48', 'core/src/main/')


