from context import ROOT_DIR, entityUtils

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
		self.TEMP = os.path.join(ROOT_DIR, 'data_construction/repository_miner/TEMP/')

		# Files
		self.HISTORY_CLASS    = os.path.join(ROOT_DIR, 'data/history/class_changes/' + self.systemName + '.csv')
		self.HISTORY_METHOD   = os.path.join(ROOT_DIR, 'data/history/method_changes/' + self.systemName + '.csv')
		self.ENTITY_CLASS     = os.path.join(ROOT_DIR, 'data/entities/classes/' + self.systemName + '.csv')
		self.ENTITY_CLASS_ALL = os.path.join(ROOT_DIR, 'data/entities/classes_all/' + self.systemName + '.csv')
		self.ENTITY_METHOD    = os.path.join(ROOT_DIR, 'data/entities/methods/' + self.systemName + '.csv')

		if not os.path.exists(self.TEMP):
			os.makedirs(self.TEMP)

		#cloneCommand = 'git clone ' + self.repositoryURL + ' ' + self.TEMP + self.systemName
		#subprocess.call(cloneCommand, shell=True)

		self.cwd = os.getcwd()
		os.chdir(self.TEMP + self.systemName)
		subprocess.call('git checkout -f '+ self.snapshot, shell=True)


	#close before extracting historical information for another system
	def close(self):
		os.chdir(self.cwd)

		# Remove the TEMP directory
		#subprocess.call("rm -rf " + self.TEMP, shell=True)

	def mine(self, system):
		self.setup(system)

		#he = history_extractor.HistoryExtractor()

		#he.createHistoryFile(self.HISTORY_CLASS, "C")
		#self.__correctExceptions(self.HISTORY_CLASS, he.exceptionDirs, he.package_dirs_dictionary)
		#he.createHistoryFile(self.HISTORY_METHOD, "M")

		#self.__createClassFiles(he.package_dirs_dictionary)
		#self.__createMethodFile(self.ENTITY_METHOD, he.package_dirs_dictionary)

		#self.__createMetricsFile("DECOR")
		#self.__createMetricsFile("INCODE")
		#self.__createMetricsFile("JDEODORANT")


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
					name = entityUtils.getClassName(os.path.join(direc,f))
					mainClass = package + '.' + name
					F1.write(mainClass + '\n')

					classes = entityUtils.getClassesInFile(os.path.join(direc,f))
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
					methods = entityUtils.getMethodsInFile(os.path.join(direc,f))

					for methodName in methods:
						normalizedMethodName = entityUtils.normalizeMethodName(methodName)
						F.write(package + '.' + normalizedMethodName + '\n')

		F.close()


	# This method is used to create the metrics files necessary to compute Decor ant InCode confidence metrics 
	def __createMetricsFile(self, tool):
		assert tool in ["DECOR", "INCODE", "JDEODORANT"], tool + " is not a valid tool"

		if tool == "DECOR":
			metricFile = os.path.join(ROOT_DIR, 'data/metric_files/decor/' + self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets/jar/DecorMetricsFileCreator.jar')
			directories = "@".join(self.mainDirectories)
		
		if tool == "INCODE":
			metricFile = os.path.join(ROOT_DIR, 'data/metric_files/incode/' + self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets/jar/InCodeMetricsFileCreator.jar')
			directories = "@".join(self.sources)
		
		if tool == "JDEODORANT":
			metricFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/feature_envy_metrics/' + self.systemName + '.csv')
			jarFile = os.path.join(ROOT_DIR, 'assets/jar/JDMetricsFileCreator.jar')
			directories = "@".join(self.sources)


		repositoryPath = self.TEMP + self.systemName + "/"

		createCommand = "java -jar " + jarFile + " " + self.systemName + " " + repositoryPath + " " + directories + " " + metricFile
		subprocess.call(createCommand, shell=True)


if __name__ == "__main__":

	systms = [
		{
		"name"     :'apache-derby', 
		"url"      :'https://github.com/apache/derby.git', 
		"snapshot" :'c30c7da', 
		"directory":['java/engine/'],
		"sources"  :['java/engine/']
		},
		{
		"name"     :'apache-jena',
		"url"      :'https://github.com/apache/jena.git',
		"snapshot" :'dc0bfe6f0d32de82f711bc241e8f96e2be0a539d',
		"directory":['jena-core/src/main/java/'],
		"sources"  :['jena-core/src/main/java/']
		},
		{
		"name"     :'apache-log4j2', 
		"url"      :'https://github.com/apache/log4j.git', 
		"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
		"directory":['src/java/'],
		"sources"  :['src/java/']
		},
		{
		"name"     :'apache-velocity',
		"url"      :'https://github.com/apache/velocity-engine.git',
		"snapshot" :'23c979d3b185ace79c06fc7bedfcc1b9c232eb06',
		"directory":['src/java/'],
		"sources"  :['src/java/']
		},
		{
		"name"     :'javacc',
		"url"      :'https://github.com/javacc/javacc.git',
		"snapshot" :'1b23b61777df9ccfe627682c848a07b3bf73387b',
		"directory":['src/main/java/'],
		"sources"  :['src/main/java/']
		},
		{
		"name"     :'jgraphx', 
		"url"      :'https://github.com/jgraph/jgraphx.git', 
		"snapshot" :'25c9cfc539564de53d71a022815f3033630ba7c2', 
		"directory":['src/'],
		"sources"  :['src/']

		},
		{
		"name"     :'jgroups',
		"url"      :'https://github.com/belaban/JGroups.git',
		"snapshot" :'2d2ee7db9763c527a0228ba95dba433a2ea11972',
		"directory":['src/'],
		"sources"  :['src/']
		},
		{
		"name"     :'jhotdraw', 
		"url"      :'https://svn.code.sf.net/p/jhotdraw/svn/trunk', 
		"snapshot" :'58d8df336c3c48a1943427754f6bbb6e991c2e41', 
		"directory":['jhotdraw7/src/main/java/'],
		"sources"  :['jhotdraw7/src/main/java/']
		},
		{
		"name"     :'jspwiki', 
		"url"      :'https://github.com/apache/jspwiki.git', 
		"snapshot" :'a3b1041393db03d72d32e4d51554941be55e07e3', 
		"directory":['src/'],
		"sources"  :['src/']
		},
		{
		"name"     :'junit', 
		"url"      :'https://github.com/junit-team/junit4.git', 
		"snapshot" :'751f75986b11336ac8310d73c89003b0b09ecb92', 
		"directory":['src/main/java/'],
		"sources"  :['src/main/java/']
		},
		{
		"name"     :'mongodb', 
		"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
		"snapshot" :'b67c0c43', 
		"directory":['src/main/'],
		"sources"  :['src/main/']
		},
		{
		"name"     :'pmd', 
		"url"      :'https://github.com/pmd/pmd.git', 
		"snapshot" :'6063aaf', 
		"directory":['pmd/src/main/java/'],
		"sources"  :['pmd/src/main/java/']
		},
	]


	rm = RepositoryMiner()

	for system in systms:
		rm.mine(system)

