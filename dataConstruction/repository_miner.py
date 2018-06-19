import fnmatch
import os
import subprocess
import systems

import history_extractor
import entityUtils

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
		self.TEMP = os.path.dirname(os.path.abspath(__file__)) + '/TEMP/'

		# Files
		self.HISTORY_CLASS    = os.path.dirname(os.path.abspath(__file__)) + '/../data/history/class_changes/' + self.systemName + '.csv'
		self.HISTORY_METHOD   = os.path.dirname(os.path.abspath(__file__)) + '/../data/history/method_changes/' + self.systemName + '.csv'
		self.ENTITY_CLASS     = os.path.dirname(os.path.abspath(__file__)) + '/../data/entities/classes/' + self.systemName + '.csv'
		self.ENTITY_CLASS_ALL = os.path.dirname(os.path.abspath(__file__)) + '/../data/entities/classes_all/' + self.systemName + '.csv'
		self.ENTITY_METHOD    = os.path.dirname(os.path.abspath(__file__)) + '/../data/entities/methods/' + self.systemName + '.csv'

		if not os.path.exists(self.TEMP):
			os.makedirs(self.TEMP)

		cloneCommand = 'git clone ' + self.repositoryURL + ' ' + self.TEMP + self.systemName
		subprocess.call(cloneCommand, shell=True)

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
		#self.__createMethodFile(he.package_dirs_dictionary)

		#self.__createMetricsFile("GC")
		self.__createMetricsFile("FE")

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

	def __createMethodFile(self, package_dirs_dictionary):
		F = open(self.ENTITY_METHOD, 'w') 
		
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
	def __createMetricsFile(self, smell):
		if smell == "GC":
			smellDir = "god_class/Decor"
			jarFile = self.TEMP + "../../advisors/metrics_files_generators/Decor/jar/GodClassMetricsFileCreator.jar"
			directories = "@".join(self.mainDirectories)
		elif smell == "FE":
			smellDir = "feature_envy/InCode"
			jarFile = self.TEMP + "../../advisors/metrics_files_generators/InCode/jar/FeatureEnvyMetricsFileCreator.jar"
			directories = "@".join(self.sources)
		else:
			print(smell + " is not a valid smell")
			return

		repositoryPath = self.TEMP + self.systemName + "/"
		metricsFile = self.TEMP + "../../advisors/metrics_files/"+ smellDir + "/" + self.systemName + '.csv'

		createCommand = "java -jar " + jarFile + " " + self.systemName + " " + repositoryPath + " " + directories + " " + metricsFile
		subprocess.call(createCommand, shell=True)


if __name__ == "__main__":

	'''system = {
	"name"     :'jedit',
	"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
	"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
	"directory":['']
	}

	rm.mine(system)'''

