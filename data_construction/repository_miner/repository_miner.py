from context import ROOT_DIR

import utils.java_utils as java_utils

import fnmatch
import os
import subprocess
import systems
import history_extractor

class RepositoryMiner(object):
	def __init__(self, system = None):
		if system is not None:
			self.setup(system)

	def setup(self, system):
		self.repositoryURL   = system['url']
		self.systemName      = system['name']
		self.snapshot        = system['snapshot']
		self.mainDirectories = system['directory']
		self.sources         = system['sources']

		# Directories
		self.TEMP = os.path.join(ROOT_DIR, 'data_construction', 'repository_miner', 'TEMP')

		# Files
		self.HISTORY_CLASS    = os.path.join(ROOT_DIR, 'approaches', 'hist', 'history', 'class_changes', self.systemName + '.csv')
		self.HISTORY_METHOD   = os.path.join(ROOT_DIR, 'approaches', 'hist', 'history', 'method_changes', self.systemName + '.csv')
		self.ENTITY_CLASS     = os.path.join(ROOT_DIR, 'data', 'entities', 'classes', self.systemName + '.csv')
		self.ENTITY_CLASS_ALL = os.path.join(ROOT_DIR, 'data', 'entities', 'classes_all', self.systemName + '.csv')
		self.ENTITY_METHOD    = os.path.join(ROOT_DIR, 'data', 'entities', 'methods', self.systemName + '.csv')

		if not os.path.exists(self.TEMP):
			os.makedirs(self.TEMP)

		cloneCommand = 'git clone ' + self.repositoryURL + ' ' + os.path.join(self.TEMP, self.systemName)
		subprocess.call(cloneCommand, shell=True)

		self.cwd = os.getcwd()
		os.chdir(os.path.join(self.TEMP, self.systemName))
		subprocess.call('git checkout -f '+ self.snapshot, shell=True)


	#close before extracting historical information for another system
	def close(self):
		os.chdir(self.cwd)

		# Remove the TEMP directory
		subprocess.call("rm -rf " + self.TEMP, shell=True)

	def mine(self, system):
		self.setup(system)

		he = history_extractor.HistoryExtractor()

		he.createHistoryFile(self.HISTORY_CLASS, "C")
		self.__correctExceptions(self.HISTORY_CLASS, he.exceptionDirs, he.package_dirs_dictionary)
		he.createHistoryFile(self.HISTORY_METHOD, "M")

		self.__createClassFiles(he.package_dirs_dictionary)
		self.__createMethodFile(self.ENTITY_METHOD, he.package_dirs_dictionary)

		self.__createMetricsFile("DECOR")
		self.__createMetricsFile("INCODE")
		self.__createMetricsFile("JDEODORANT")


		self.close()

	# This method is used to replace occurences of exeptionsDirs by their correspondind package name
	# in entity files and history files.
	# In case the program first failed to assign a package to a directory but succeeded in a later commit.
	def __correctExceptions(self, filePath, exceptionDirs, package_dirs_dictionary):
		with open(filePath, 'r+') as file:
			fileString = file.read()
			
			for d in set(exceptionDirs):
				if d in package_dirs_dictionary:
					fileString = fileString.replace(d, package_dirs_dictionary[d])

			file.seek(0)
			file.write(fileString)
			file.truncate()


	#create a csv file containing all the classes/methods contained in the main directory
	def __createClassFiles(self, package_dirs_dictionary):
		F1 = open(self.ENTITY_CLASS, 'w')
		F2 = open(self.ENTITY_CLASS_ALL, 'w')

		F2.write("Path;Entity\n")
		for directory in ['./' + d for d in self.mainDirectories]:
			for path,dirs,files in os.walk(directory):
				direc = path[2:len(path) + 1]
				if direc in package_dirs_dictionary:
					package = package_dirs_dictionary[direc]
				else:
					package = direc

				for f in fnmatch.filter(files,'*.java'):
					name = java_utils.getClassName(os.path.join(direc,f))
					mainClass = package + '.' + name
					F1.write(mainClass + '\n')

					classes = java_utils.getClassesInFile(os.path.join(direc,f))
					for klass in classes:
						F2.write(os.path.join(direc,f) + ';' + package + '.' + klass + '\n')

		F1.close()
		F2.close()

	def __createMethodFile(self, methodFile, package_dirs_dictionary):
		F = open(methodFile, 'w') 
		
		for directory in ['./' + d for d in self.mainDirectories]:
			for path,dirs,files in os.walk(directory):
				direc = path[2:len(path) + 1]
				if direc in package_dirs_dictionary:
					package = package_dirs_dictionary[direc]
				else:
					package = direc

				for f in fnmatch.filter(files,'*.java'):
					methods = java_utils.getMethodsInFile(os.path.join(direc,f))

					for methodName in methods:
						normalizedMethodName = java_utils.normalizeMethodName(methodName)
						F.write(package + '.' + normalizedMethodName + '\n')

		F.close()


	# This method is used to create the metrics files necessary to compute Decor ant InCode confidence metrics 
	def __createMetricsFile(self, tool):
		assert tool in ["DECOR", "INCODE", "JDEODORANT"], tool + " is not a valid tool"

		if tool == "DECOR":
			metricFile = os.path.join(ROOT_DIR, 'approaches', 'decor', 'metric_files', self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets', 'jar', 'DecorMetricsFileCreator.jar')
			directories = "@".join(self.mainDirectories)
		
		if tool == "INCODE":
			metricFile = os.path.join(ROOT_DIR, 'approaches', 'incode', 'metric_files', self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets', 'jar', 'InCodeMetricsFileCreator.jar')
			directories = "@".join(self.sources)
		
		if tool == "JDEODORANT":
			metricFile = os.path.join(ROOT_DIR, 'approaches', 'jdeodorant', 'metric_files', 'feature_envy_metrics', self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets', 'jar', 'JDMetricsFileCreator.jar')
			directories = "@".join(self.sources)


		repositoryPath = os.path.join(self.TEMP, self.systemName)

		createCommand = "java -jar " + jarFile + " " + self.systemName + " " + repositoryPath + "/ " + directories + " " + metricFile
		subprocess.call(createCommand, shell=True)
