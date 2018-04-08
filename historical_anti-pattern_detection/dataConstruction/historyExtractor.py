# -*- coding: utf-8 -*-
import subprocess
import os
import fnmatch
import urllib2
import json, ast
import progressbar
import re
import javalang
import time

import systems

''' Class used to extract history information from the versionning systems of the differents sofwares.
	All this data will be stored in csv files. '''


class HistoryExtractor(object):
	def __init__(self, system = None):
		if system is not None:
			self.setup(system)

	def setup(self, system):
		self.repositoryURL = system['url']
		self.systemName = system['name']
		self.snapshot = system['snapshot']
		self.mainDirectorys = system['directory']

		#dictionary making correspondance between paths and class names
		#   to reduce execution time
		self.path_name_dictionary = {}

		#the paths for which the program failed to return a class name
		self.exceptionPaths = []

		cloneCommand = 'git clone ' + self.repositoryURL + ' ' + self.systemName
		subprocess.call(cloneCommand, shell=True)

		self.cwd = os.getcwd()
		os.chdir(self.systemName)
		subprocess.call('git checkout -f '+ self.snapshot, shell=True)

	#close before extracting historical information for another system
	def close(self):
		subprocess.call('git checkout master', shell=True)
		os.chdir(self.cwd)

		removeDirCommand = "rm -rf " + self.systemName
		subprocess.call(removeDirCommand, shell=True)

	def extractChangeHistory(self, granularity = "C"):
		if granularity == "C":
			instanceFilePath = self.cwd + '/../data/instances/classes/' + self.systemName + '.csv'
			historyFilePath = self.cwd + '/../data/history/class_changes/' + self.systemName + '.csv'

		if granularity == "M":
			instanceFilePath = self.cwd + '/../data/instances/methods/' + self.systemName + '.csv'
			historyFilePath = self.cwd + '/../data/history/method_changes/' + self.systemName + '.csv'

		self.__createInstanceFile(instanceFilePath, granularity)
		self.__createHistoryFile(historyFilePath, granularity)

		self.__addMissingNames(instanceFilePath)
		self.__addMissingNames(historyFilePath)


	# this method is used to replace occurences of exeptionsPaths by their correspondind names
	# in instances files and history files.
	# in case the program first failed to assign a name to a path but succeeded in a later commit.
	def __addMissingNames(self, filePath):
		with open(filePath, 'r+') as file:
			fileString = file.read()

			for path in set(self.exceptionPaths):
				if path in self.path_name_dictionary:
					fileString = fileString.replace(path, self.path_name_dictionary[path])

			file.seek(0)
			file.write(fileString)
			file.truncate()


	def __createHistoryFile(self, historyFilePath, granularity):
		F = open(historyFilePath, 'w')
		if granularity == 'C':
			F.write('Snapshot;Date;Directory;Code;ChangeType\n')
		if granularity == 'M':
			F.write('Snapshot;Date;Class;Code;ChangeType\n')

		ps1 = subprocess.Popen(['git','log','--pretty=format:%H_%aD'], stdout=subprocess.PIPE)
		output1, error1 = ps1.communicate()

		commits = output1.split('\n')

		count = 0
		bar = progressbar.ProgressBar(maxval=len(commits), \
			widgets=['writing history file : ' ,progressbar.Percentage()])
		bar.start()

		options = {"C": self.__getClassChange, "M": self.__getMethodeChange}

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
					changeType = fileChange.split()[0]
					filePath = fileChange.split()[1]

					change = options[granularity](SHA, date, filePath, changeType)
					F.write(change)

		subprocess.call("rm -f ../previousFile.java", shell=True)
		subprocess.call("rm -f ../actualFile.java", shell=True)

		bar.finish()
		F.close()


	#create a csv file containing all the classes/methods contained in the main directory
	def __createInstanceFile(self, filePath, granularity):
		F = open(filePath, 'w')
		
		for directory in self.mainDirectorys:
			for path,dirs,files in os.walk('./' + directory):
				for f in fnmatch.filter(files,'*.java'):
					try:
						className = self.__getClassName(os.path.join(path,f)[2:])
					except:
						className = os.path.join(path,f)[2:]

					if granularity == "C":
						F.write(className + '\n')

					if granularity == "M":
						try:
							methods = self.__getMethodsInFile(os.path.join(path,f))
						except:
							methods = self.__getMethodsInFileWithRegex(os.path.join(path,f))

						for methodName in methods:
							F.write(className + '.' + methodName + '\n')

		F.close()


	def __getClassChange(self, SHA, date, filePath, changeType):
		if filePath in self.path_name_dictionary:
			className = self.path_name_dictionary[filePath]
		else:
			try:
				if os.path.isfile(filePath):
					className = self.__getClassName(filePath)
				else:
					if changeType == 'D':
						self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")
						className = self.__getClassName(filePath, "../previousFile.java")
				
					else:
						self.__updateWorkingFile("../actualFile.java", filePath, SHA)
						className = self.__getClassName(filePath, "../actualFile.java")

				self.path_name_dictionary[filePath] = className
			except:
				className = filePath
				self.exceptionPaths.append(filePath)

		directory = self.__getClassDirectory(filePath)

		line = SHA + ';' + date + ';' + directory + ';' + className + ';' + changeType + '\n'
		return line


	def __getClassName(self, filePath, wFilePath = None):
		if wFilePath is not None:
			java_source = open(wFilePath, 'r')
		else:
			java_source = open(filePath, 'r')

		tree = javalang.parse.parse(java_source.read())
		package = tree.package.name

		name = filePath.split('/')[-1]
		name = name[:len(name)-len('.java')]

		return package + '.' + name

	def __getClassDirectory(self, filePath):
		directory = filePath.split('/')
		directory.pop()
		
		return '/'.join(directory)


	def __getMethodeChange(self, SHA, date, filePath, changeType):
		changes = []

		if changeType == "A":
			self.__updateWorkingFile("../actualFile.java", filePath, SHA)
			try:
				methods = self.__getMethodsInFile(filePath, "../actualFile.java")
			except:
				methods = self.__getMethodsInFileWithRegex("../actualFile.java")

			for method in methods:
				change = method + ";" + "ADDED"
				changes.append(change)

		if changeType == "D":
			self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")
			try:
				methods = self.__getMethodsInFile(filePath, "../previousFile.java")
			except:
				methods = self.__getMethodsInFileWithRegex("../previousFile.java")
		
			for method in methods:
				change = method + ";" + "DELETED"
				changes.append(change)

		if changeType == "M":
			self.__updateWorkingFile("../actualFile.java", filePath, SHA)
			self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")

			diffjCommand = "java -jar ../../assets/frameworks/diffj-1.6.3.jar --brief ../previousFile.java ../actualFile.java"
			ps = subprocess.Popen(diffjCommand.split(), stdout=subprocess.PIPE)
			output, error = ps.communicate()

			diffs = output.split('\n')

			for line in diffs:
				method, ct = self.__parseLine(line)

				if ct is not None:
					# store change like that, so it is hashable
					change = method + ";" + ct
					changes.append(change)


		lines = ""

		className = ""
		if filePath in self.path_name_dictionary:
			className = self.path_name_dictionary[filePath]
		else:
			try:
				if os.path.isfile(filePath):
					className = self.__getClassName(filePath)
				else:
					if changeType == 'D':
						self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")
						className = self.__getClassName(filePath, "../previousFile.java")
				
					else:
						self.__updateWorkingFile("../actualFile.java", filePath, SHA)
						className = self.__getClassName(filePath, "../actualFile.java")

				self.path_name_dictionary[filePath] = className
			except:
				className = filePath
				self.exceptionPaths.append(filePath)


		for change in set(changes):
			lines = lines + SHA + ';' + date + ';' + className + ';' + className + '.' + change + '\n'

		return lines


	def __getMethodsInFile(self, filePath, wFilePath=None):
		className = filePath.split('/')[-1]
		className = name[:len(name)-len('.java')]

		if wFilePath is not None:
			java_source = open(wFilePath, 'r')
		else:
			java_source = open(filePath, 'r')

		tree = javalang.parse.parse(java_source.read())
		
		InnerClassMethods = []
		for pc, klass in tree.filter(javalang.tree.ClassDeclaration):
			if klass.name != className:
				for p, method in klass.filter(javalang.tree.MethodDeclaration):
					InnerClassMethods.append(method)
			
		methods = []
		for p, method in tree.filter(javalang.tree.MethodDeclaration):
			if method not in InnerClassMethods:
				name = method.name
				parameters = []
				hasNext = False
				for path, node in method:
					if hasNext == True:
						if issubclass(type(node), javalang.tree.Type) & hasNext:
							hasNext = False
							parameters.append(node.name)
					else:
						if type(node) == javalang.tree.FormalParameter:
							hasNext = True

				string = name + '('
				for i, param in enumerate(parameters):
					if i < len(parameters)-1:
						string = string + param + ', '
					else:
						string = string + param
				string = string + ')'
				methods.append(string)

		return methods

	#works but does not ignore methods from inner classes
	def __getMethodsInFileWithRegex(self, filePath):
		regex = '((public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\)\s*(\{))'

		methods = []
		with open(filePath, 'r') as javaFile:
			content = javaFile.read()
			m = re.findall(regex, content)
			for method in m:
				name = re.search('(\w+) *\([^\)]*\)', method[0]).groups()[0]
				params = re.search('\w+ *(\([^\)]*\))', method[0]).groups()[0]
				params = re.sub('\s+', ' ', params)
				params = params[1:-1].split(", ")
				params = [p.split(' ')[0] for p in params]
				params = '(' + ', '.join(params) + ')'
				
				string = name + params
				methods.append(string)

		return methods


	def __parseLine(self, line):
		match = re.search('\w+ *\([^\)]*\)', line)
		method = ""
		if match is not None:
			method = match.group(0)
		ct = None

		if re.search('method removed', line) is not None:
			ct = "REMOVED"

		if re.search('method added', line) is not None:
			ct = "ADDED"

		if re.search('code \w* in', line) is not None:
			ct = "BODY_MODIFIED"

		#code removed in createAntlib(Project, URL, String)
		#code added in createAntlib(Project, URL, String)
		return method, ct


	def __updateWorkingFile(self, wFilePath, filePath, SHA):
		F = open(wFilePath, "w")

		fileCommand = "git show " + SHA + ":" + filePath 
		ps = subprocess.Popen(fileCommand.split(), stdout=subprocess.PIPE)
		file, error = ps.communicate()

		F.write(file)
		F.close()




if __name__ == "__main__":
	
	'''
	he = HistoryExtractor()
	for system in systems.systems_git:
		he.setup(system)
		he.extractChangeHistory("C")
		he.close()

	for system in systems.systems_svn:
		he.setup(system)
		he.extractChangeHistory("C")
		he.close()'''

	s = {
	"name"     :'jhotdraw', 
	"url"      :'https://svn.code.sf.net/p/jhotdraw/svn/trunk', 
	"snapshot" :'58d8df336c3c48a1943427754f6bbb6e991c2e41', 
	"directory":['jhotdraw7/src/main/']
	}

	he = HistoryExtractor()
	he.setup(s)
	he.extractChangeHistory("M")
	#he.close()







	