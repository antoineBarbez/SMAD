from context import ROOT_DIR

import utils.java_utils as java_utils

import javalang
import os
import progressbar
import re
import subprocess


class HistoryExtractor(object):
	def __init__(self):
		# Dictionary making correspondence between file paths and class names,
		# to reduce execution time
		self.package_dirs_dictionary = {}

		# The paths for which the program failed to return a package name
		self.exceptionDirs = []


	def createHistoryFile(self, historyFilePath, granularity):
		F = open(historyFilePath, 'w')
		F.write('Snapshot;Date;Entity;ChangeType\n')

		ps1 = subprocess.Popen(['git','log','--pretty=format:%H_%aD'], stdout=subprocess.PIPE)
		output1, error1 = ps1.communicate()

		commits = output1.split('\n')

		count = 0
		gra = {"C": "Class", "M": "Method"}
		bar = progressbar.ProgressBar(maxval=len(commits), \
			widgets=['writing ' + gra[granularity] + ' history file : ' ,progressbar.Percentage()])
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

		bar.finish()
		F.close()


	def __getClassChange(self, SHA, date, filePath, changeType):
		directory = java_utils.getDirectory(filePath)
		if directory in self.package_dirs_dictionary:
			package = self.package_dirs_dictionary[directory]
		else:
			try:
				if os.path.isfile(filePath):
					package = java_utils.getPackage(filePath)
				else:
					if changeType == 'D':
						self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")
						package = java_utils.getPackage("../previousFile.java")
				
					else:
						self.__updateWorkingFile("../actualFile.java", filePath, SHA)
						package = java_utils.getPackage("../actualFile.java")
			except (javalang.tokenizer.LexerError, javalang.parser.JavaSyntaxError, AttributeError):
				package = directory
				self.exceptionDirs.append(directory)
			except:
				raise
			else:
				self.package_dirs_dictionary[directory] = package


		line = SHA + ';' + date + ';' + package + '.' + java_utils.getClassName(filePath) + ';' + changeType + '\n'
		return line


	def __getMethodeChange(self, SHA, date, filePath, changeType):
		directory = java_utils.getDirectory(filePath)
		if directory in self.package_dirs_dictionary:
			package = self.package_dirs_dictionary[directory]
		else:
			package = directory

		changes = []
		if changeType == "M":
			self.__updateWorkingFile("../actualFile.java", filePath, SHA)
			self.__updateWorkingFile("../previousFile.java", filePath, SHA + "^")

			diffj_jar = os.path.join(ROOT_DIR, 'assets', 'jar', 'diffj-1.6.3.jar')

			diffjCommand = "java -jar " + diffj_jar + " --brief ../previousFile.java ../actualFile.java"
			ps = subprocess.Popen(diffjCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, error = ps.communicate()

			diffs = output.split('\n')
			actual_method_class_dictionary   = None
			previous_method_class_dictionary = None
			for line in diffs:
				method, ct = self.__parseLine(line)

				if (ct == "ADDED") | (ct == "BODY_MODIFIED"):
					if actual_method_class_dictionary is None:
						actual_method_class_dictionary = java_utils.getMethodClassDictionary("../actualFile.java")

					method = java_utils.normalizeMethodName(method)
					if (method in actual_method_class_dictionary):
						method = actual_method_class_dictionary[method] + '.' + method

						# store change like that, so it is hashable
						change = method + ";" + ct
						changes.append(change)

				if ct == "DELETED":
					if previous_method_class_dictionary is None:
						previous_method_class_dictionary = java_utils.getMethodClassDictionary("../previousFile.java")

					method = java_utils.normalizeMethodName(method)
					if (method in previous_method_class_dictionary):
						method = previous_method_class_dictionary[method] + '.' + method

						# Store change like that, so it is hashable
						change = method + ";" + ct
						changes.append(change)


		lines = ""
		for change in set(changes):
			lines = lines + SHA + ';' + date + ';' + package + '.' + change + '\n'

		return lines


	def __parseLine(self, line):
		match = re.search('\w+ *\([^\)]*\)', line)
		method = None
		ct = None

		if match is not None:
			method = match.group(0)

			if re.search('method removed', line) is not None:
				ct = "DELETED"

			if re.search('method added', line) is not None:
				ct = "ADDED"

			if re.search('code \w* in', line) is not None:
				ct = "BODY_MODIFIED"

		return method, ct


	def __updateWorkingFile(self, wFilePath, filePath, SHA):
		F = open(wFilePath, "w")

		fileCommand = "git show " + SHA + ":" + filePath 
		ps = subprocess.Popen(fileCommand.split(), stdout=subprocess.PIPE)
		file, error = ps.communicate()

		F.write(file)
		F.close()
