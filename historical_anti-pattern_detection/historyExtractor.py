# -*- coding: utf-8 -*-
import subprocess
import os
import fnmatch
import urllib2
import json, ast
import progressbar


''' Methods used to extract history information from the versionning systems of the differents sofwares,
	and extract the anti-pattern occurences from the landfill database (http://www.sesa.unisa.it/landﬁll/).
	all this data will be stored in csv files. '''

def getMethodeName(methodePath, mainDirectory):
	methode = methodePath[len(mainDirectory):]
	methode = methode[:len(methode)-len('.java')]
	methode = '.'.join(methode.split('/'))

	return methode 


def createHistoryFile(mainDirectory, historyFilePath):
	F = open(historyFilePath, 'w')
	F.write('Snapshot;Date;Entity;Code;ChangeType\n')

	ps1 = subprocess.Popen(['git','log','--pretty=format:%H_%aD'], stdout=subprocess.PIPE)
	output1, error1 = ps1.communicate()

	commits = output1.split('\n')

	count = 0
	bar = progressbar.ProgressBar(maxval=len(commits), \
		widgets=['writing history file : ' ,progressbar.Percentage()])
	bar.start()

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
					methode = getMethodeName(fileChange.split()[1], mainDirectory)

					line = SHA + ';' + date + ';' + 'CLASS' + ';' + methode + ';' + fileChange.split()[0] + '\n'
					F.write(line)

	bar.finish()
	F.close()

#create a csv file containing all the methods contained in the main directory
def createMethodsFile(mainDirectory, methodsFilePath):
	F = open(methodsFilePath, 'w')
	
	for path,dirs,files in os.walk('./' + mainDirectory):
		for f in fnmatch.filter(files,'*.java'):
			methode = getMethodeName(os.path.join(path,f)[2:], mainDirectory)
			F.write(methode + '\n')

	F.close()


def extractChangeHistory(repositoryURL, systemName, snapshot, mainDirectory):
	cloneCommand = 'git clone ' + repositoryURL + ' ' + systemName
	subprocess.call(cloneCommand, shell=True)

	cwd = os.getcwd()
	os.chdir(systemName)
	subprocess.call('git checkout -f '+ snapshot, shell=True)

	methodsFile = cwd + '/data/systems_methods/' + systemName + '.csv'
	historyFile = cwd + '/data/systems_history/' + systemName + '.csv'
	createMethodsFile(mainDirectory, methodsFile)
	createHistoryFile(mainDirectory, historyFile)

	subprocess.call('git checkout master', shell=True)
	os.chdir(cwd)

	removeDirCommand = "rm -rf " + systemName
	subprocess.call(removeDirCommand, shell=True)

def createSmellFile(systemName, systemId, smell):
	url = 'http://www.sesa.unisa.it/landfill/GetBadSmells?system=' + str(systemId) +'&type=' + smell
	response = urllib2.urlopen(url)
	data = ast.literal_eval(json.dumps(json.load(response)))

	fileName = './data/anti-pattern_occurences/'+ smell + '/' + systemName + '.csv'
	F = open(fileName, 'w')

	for occurence in data['data']:
		methode = occurence['instance']
		F.write(methode + '\n')

	F.close()


def extractSmellOccurences():
	response = urllib2.urlopen('http://www.sesa.unisa.it/landfill/GetSystems?datasetId=1')
	data = ast.literal_eval(json.dumps(json.load(response)))

	for system in data:
		systemName = '-'.join(system['name'].lower().split())
		for smell in system['types']:
			directoryPath = './data/anti-pattern_occurences/'+ smell['type']
			if not os.path.exists(directoryPath):
				os.makedirs(directoryPath)

			createSmellFile(systemName, system['id'], smell['type'])



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
	#extractChangeHistory('https://github.com/apache/karaf.git', 'apache-log4j', '7cf64b6c9692e596193a0b11e38367721cf1c938', '')

	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'apache-ant', '6e34f177ee9e41ba3d066b6a4c92b21dbdf28804', 'src/main/')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/cassandra.git', 'apache-cassandra', '4db577abf8e0cfda655d16abc5d99aeaafba02d0', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/hive.git', 'apache-hive', 'ddd32a12693c1231545fc9540d626fde01cdae4b', '')
	#extractChangeHistory('https://github.com/apache/log4j', 'apache-log4j', '7cf64b6c9692e596193a0b11e38367721cf1c938', 'src/main/java/')
	#extractChangeHistory('https://github.com/apache/lucene-solr.git', 'apache-lucene', '5036d7ca5fbb08643d6535ee84ed78e540dc2e54', '')
	#extractChangeHistory('https://gitbox.apache.org/repos/asf/nutch.git', 'apache-nutch', '56cab894436348e7fbb9bbc8f5ff014bd73fdc20', 'src/java/')
	#extractChangeHistory('git://git.apache.org/pig.git', 'apache-pig', 'a8c680cf28ad4c2ab824c268a3dbe2783667dd94', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'apache-qpid', 'f71f9dfdca4372648b896c0b9b51a78f4ce61b5d', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'apache-struts', '9ad9404bfac2b936e1b5f0f5e828335bc5a51b48', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'apache-xerces', '162649b707d5b28e7b7a4659fd2fdcd80c9c1ae8', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'agro-uml', '1092', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'atunes', '872', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'eclipse-jdt-core', '872', '')
	#extractChangeHistory('https://git.code.sf.net/p/freemind/code', 'freemind', '544', 'freemind/')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'hsqldb', '881', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'jedit', '281', '')
	#extractChangeHistory('https://git-wip-us.apache.org/repos/asf/ant.git', 'jhotdraw', '817', '')

