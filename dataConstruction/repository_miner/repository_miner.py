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
		self.TEMP = os.path.dirname(os.path.abspath(__file__)) + '/TEMP/'

		# Files
		self.HISTORY_CLASS    = ROOT_DIR + '/data/history/class_changes/' + self.systemName + '.csv'
		self.HISTORY_METHOD   = ROOT_DIR + '/data/history/method_changes/' + self.systemName + '.csv'
		self.ENTITY_CLASS     = ROOT_DIR + '/data/entities/classes/' + self.systemName + '.csv'
		self.ENTITY_CLASS_ALL = ROOT_DIR + '/data/entities/classes_all/' + self.systemName + '.csv'
		self.ENTITY_METHOD    = ROOT_DIR + '/data/entities/methods/' + self.systemName + '.csv'

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
		#self.__createMethodFile(self.ENTITY_METHOD, he.package_dirs_dictionary)

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
	def __createMetricsFile(self, smell):
		if smell == "GC":
			smellDir = "god_class/Decor"
			jarFile = self.TEMP + "/../../../detection_tools/metrics_files_generators/Decor/jar/GodClassMetricsFileCreator.jar"
			directories = "@".join(self.mainDirectories)
		elif smell == "FE":
			smellDir = "feature_envy/InCode"
			jarFile = self.TEMP + "/../../../detection_tools/metrics_files_generators/InCode/jar/FeatureEnvyMetricsFileCreator.jar"
			directories = "@".join(self.sources)
		else:
			print(smell + " is not a valid smell")
			return

		repositoryPath = self.TEMP + self.systemName + "/"
		metricsFile = self.TEMP + "../../detection_tools/metrics_files/"+ smellDir + "/" + self.systemName + '.csv'

		createCommand = "java -jar " + jarFile + " " + self.systemName + " " + repositoryPath + " " + directories + " " + metricsFile
		subprocess.call(createCommand, shell=True)


if __name__ == "__main__":

	systms = [
		{
		"name"     :'android-frameworks-opt-telephony', 
		"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
		"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
		"directory":['src/java/'],
		"sources"  :['src/java/']
		},
		{
		"name"     :'android-platform-support',
		"url"      :'https://android.googlesource.com/platform/frameworks/support',
		"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
		"directory":['v4'],
		"sources"  :[
						'v4/eclair/',
						'v4/froyo/',
						'v4/gingerbread/',
						'v4/honeycomb/',
						'v4/honeycomb_mr2/',
						'v4/ics/',
						'v4/ics-mr1/',
						'v4/java/',
						'v4/jellybean/'
					]
		},
		{
		"name"     :'apache-ant', 
		"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
		"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
		"directory":['src/main/'],
		"sources"  :['src/main/']
		},
		{
		"name"     :'apache-tomcat',
		"url"      :'https://github.com/apache/tomcat.git',
		"snapshot" :'398ca7ee',
		"directory":['java/org/'],
		"sources"  :['java/']

		},
		{
		"name"     :'lucene', 
		"url"      :'https://github.com/apache/lucene-solr.git', 
		"snapshot" :'39f6dc1', 
		"directory":['src/java/'],
		"sources"  :['src/java/']
		},
		{
		"name"     :'xerces-2_7_0', 
		"url"      :'https://github.com/apache/xerces2-j.git', 
		"snapshot" :'c986230', 
		"directory":['src/'],
		"sources"  :['src/']
		},
		{
		"name"     :'jedit',
		"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
		"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
		"directory":[''],
		"sources"  :['']
		},
		{
		"name"     :'argouml', 
		"url"      :'http://argouml.stage.tigris.org/svn/argouml/trunk', 
		"snapshot" :'6edc166ff845cf9926bc7dbb70d93181471552c1', 
		"directory":['src_new/org/'],
		"sources"  :['src_new/']
		}
	]



	rm = RepositoryMiner()

	for system in systems.systems_svn:
		rm.mine(system)

