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

	systems = [
		{
			"name"     :'apache-commons-logging',
			"url"      :'https://github.com/apache/commons-logging.git',
			"snapshot" :'d821ed3e',
			"directory":''
		},
		{
			"name"     :'apache-commons-lang', 
			"url"      :'https://github.com/apache/commons-lang.git', 
			"snapshot" :'f957d81625a3aa70385f50d87f036ebe2c54613f', 
			"directory":''
		},
		{
			"name"     :'apache-commons-io', 
			"url"      :'https://github.com/apache/commons-io.git',
			"snapshot" :'99c5008d71b61f84a114038b064d58c837ee7ed6',
			"directory":''
		},
		{
			"name"     :'apache-commons-codec', 
			"url"      :'https://github.com/apache/commons-codec.git', 
			"snapshot" :'c6c8ae7a', 
			"directory":''
		},
		{
			"name"     :'google-guava1',
			"url"      :'https://github.com/google/guava.git',
			"snapshot" :'e8959ed0',
			"directory":''
		},
		{
			"name"     :'google-guava2', 
			"url"      :'https://github.com/google/guava.git', 
			"snapshot" :'e7c525b3310b07221b263ff48b3978d4ed54f811', 
			"directory":''
		},
		{
			"name"     :'android-frameworks-opt-telephony', 
			"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
			"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
			"directory":''
		},
		{
			"name"     :'android-frameworks-sdk', 
			"url"      :'https://android.googlesource.com/platform/sdk', 
			"snapshot" :'04b07a76650a6ffd719c55f593b21fb1d92c84d2', 
			"directory":''
		},
		{
			"name"     :'android-platform-support',
			"url"      :'https://android.googlesource.com/platform/frameworks/support',
			"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
			"directory":''
		},
		{
			"name"     :'apache-ant', 
			"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
			"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
			"directory":'src/main/'
		},
		{
			"name"     :'apache-log4j1', 
			"url"      :'https://github.com/apache/log4j.git',
			"snapshot" :'7cf64b6c9692e596193a0b11e38367721cf1c938',
			"directory":''
		},
		{
			"name"     :'apache-log4j2', 
			"url"      :'https://github.com/apache/log4j.git', 
			"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
			"directory":''
		},
		{
			"name"     :'apache-tomcat',
			"url"      :'https://github.com/apache/tomcat.git',
			"snapshot" :'398ca7ee',
			"directory":''
		},
		{
			"name"     :'mongodb', 
			"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
			"snapshot" :'b67c0c43', 
			"directory":''
		},
		{
			"name"     :'apache-struts1', 
			"url"      :'https://github.com/apache/struts.git',
			"snapshot" :'9ad9404bfac2b936e1b5f0f5e828335bc5a51b48',
			"directory":'core/src/main/'
		},
		{
			"name"     :'apache-struts2', 
			"url"      :'https://github.com/apache/struts.git', 
			"snapshot" :'b9964b9e867c3d2512d087c87450601145a651c7', 
			"directory":'core/src/main/'
		},
		{
			"name"     :'apache-derby1', 
			"url"      :'https://github.com/apache/derby.git', 
			"snapshot" :'7a5b1d07853497727812cc9ada20209eea7b6a77', 
			"directory":''
		},
		{
			"name"     :'apache-derby2', 
			"url"      :'https://github.com/apache/derby.git', 
			"snapshot" :'fe8446d216a95529b9c165099b0d4d04c2c77be4', 
			"directory":''
		},
		{
			"name"     :'apache-cayenne1', 
			"url"      :'https://github.com/apache/cayenne.git', 
			"snapshot" :'fc5de25f422e7a8a9494a593638073215a752eae', 
			"directory":''
		},
		{
			"name"     :'apache-cayenne2', 
			"url"      :'https://github.com/apache/cayenne.git', 
			"snapshot" :'f820acff650eaa0325862efb89d316353501096f', 
			"directory":''
		},
		{
			"name"     :'junit1', 
			"url"      :'https://github.com/junit-team/junit4.git', 
			"snapshot" :'30f2b16525dabb477373be9ed3e76bb98b200806', 
			"directory":''
		},
		{
			"name"     :'junit2', 
			"url"      :'https://github.com/junit-team/junit4.git', 
			"snapshot" :'d9c908b9aab5f610e2f42aba1863ce25e36423f2', 
			"directory":''
		},
		{
			"name"     :'apache-tapestry1', 
			"url"      :'https://github.com/apache/tapestry4.git', 
			"snapshot" :'2f9be52a0001202f850a47e98a9f796759358ec8', 
			"directory":''
		},
		{
			"name"     :'apache-tapestry2', 
			"url"      :'https://github.com/apache/tapestry4.git', 
			"snapshot" :'fa9d5b3a416e60a70637a7f9c411070c517d26ca', 
			"directory":''
		},
		{
			"name"     :'cobertura1', 
			"url"      :'https://github.com/cobertura/cobertura.git', 
			"snapshot" :'0e90a9877baa84d9c9d3f4d025446eaac17fe3ad', 
			"directory":''
		},
		{
			"name"     :'cobertura2', 
			"url"      :'https://github.com/cobertura/cobertura.git', 
			"snapshot" :'7aa8877f03181e170ad638af2a3ad5e4fa68afa5', 
			"directory":''
		},
		{
			"name"     :'heritrix1', 
			"url"      :'https://github.com/internetarchive/heritrix3.git', 
			"snapshot" :'b2a0495a081c93b7f7dc5ad7f28e602134e5bf6e', 
			"directory":''
		},
		{
			"name"     :'heritrix2', 
			"url"      :'https://github.com/internetarchive/heritrix3.git', 
			"snapshot" :'18d459f6b9ebb732cda2c1d1f2ef9336e5a274dc', 
			"directory":''
		}
	]
	