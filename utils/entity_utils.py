import javalang
import re

def getClassesInFile(filePath):
	try:
		classes = getClassesInFileWithJavalang(filePath)
	except (javalang.tokenizer.LexerError, javalang.parser.JavaSyntaxError):
		classes = [getClassName(filePath)]
	except:
		raise

	return classes

# Get names of the classes defined in the file, ignore Inner Classes.
def getClassesInFileWithJavalang(filePath):
	java_source = open(filePath, 'r')
	tree = javalang.parse.parse(java_source.read())

	innerClasses = []
	for pc, klass in tree.filter(javalang.tree.ClassDeclaration):
		for pic, innerClass in klass.filter(javalang.tree.ClassDeclaration):
			if innerClass.name != klass.name:
				innerClasses.append(innerClass)

	classes = []
	for pc, klass in tree.filter(javalang.tree.ClassDeclaration):
		if klass not in innerClasses:
			classes.append(klass.name)
		
	return classes

# Get the name of the main class (the name of the file).
def getClassName(filePath):
		name = filePath.split('/')[-1]
		name = name[:len(name)-len('.java')]

		return name


def getDirectory(filePath):
	directory = filePath.split('/')
	directory.pop()
	
	return '/'.join(directory)

# Get the name of the class where a method is defined
def getEmbeddingClass(methodName):

	return '.'.join(methodName.split('.')[:-1])

def getMethodClassDictionary(filePath):
	method_class_dictionary = {}
	methods = getMethodsInFile(filePath)
	for method in methods:
		nameList = normalizeMethodName(method).split('.')
		method_class_dictionary[nameList[1]] = nameList[0]

	return method_class_dictionary 


def getMethodsInFile(filePath):
	try:
		methods = getMethodsInFileWithJavalang(filePath)
	except (javalang.tokenizer.LexerError, javalang.parser.JavaSyntaxError):
		methods = getMethodsInFileWithRegex(filePath)
	except:
		raise

	return methods

# Get the full name of the methods in the file (className.methodName).
# Inner Class methods are concidered as methods of the englobing class. 
# Interface methods are simply ignored.
# Inner Methods (methods defined inside a method) are also ignored.
def getMethodsInFileWithJavalang(filePath):
	java_source = open(filePath, 'r')
	tree = javalang.parse.parse(java_source.read())

	innerClasses = []
	for pc, klass in tree.filter(javalang.tree.ClassDeclaration):
		for pic, innerClass in klass.filter(javalang.tree.ClassDeclaration):
			if innerClass.name != klass.name:
				innerClasses.append(innerClass)

	InnerMethods  =[]
	for pm, method in tree.filter(javalang.tree.MethodDeclaration):
		for pim, innerMethod in method.filter(javalang.tree.MethodDeclaration):
			if innerMethod.name != method.name:
				InnerMethods.append(innerMethod)

	methods = []
	for pc, klass in tree.filter(javalang.tree.ClassDeclaration):
		if klass not in innerClasses:
			for pm, method in klass.filter(javalang.tree.MethodDeclaration):
				if method not in InnerMethods:
					method.name = klass.name + '.' + method.name

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

					string = method.name + '('
					for i, param in enumerate(parameters):
						if i < len(parameters)-1:
							string = string + param + ', '
						else:
							string = string + param
					string = string + ')'
					methods.append(string)

	return methods

# Works but does not take into account multiple class definition in the same file.
# To use when the file failed to be parsed.
def getMethodsInFileWithRegex(filePath):
	className = getClassName(filePath)

	regex = '((public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\)\s*(\{))'

	methods = []
	with open(filePath, 'r') as javaFile:
		content = javaFile.read()
		m = re.findall(regex, content)
		for method in m:
			methodName = re.search('(\w+) *\([^\)]*\)', method[0]).groups()[0]
			params = re.search('\w+ *(\([^\)]*\))', method[0]).groups()[0]
			params = re.sub('\s+', ' ', params)
			params = params[1:-1].split(", ")
			params = [p.split(' ')[0] for p in params]
			params = '(' + ', '.join(params) + ')'
			
			string = className + '.' + methodName + params
			methods.append(string)

	return methods


def getPackage(filePath):
	java_source = open(filePath, 'r')
	tree = javalang.parse.parse(java_source.read())
		
	return tree.package.name


def normalizeMethodName(methodName):
	m1 = re.match('(.+)\((.*)\)', methodName)

	name = m1.group(1)
	parameters = m1.group(2)
	paramList = parameters.split(', ')

	normalizedParamList = []
	for param in paramList:
		normalizedParam = param.split('.')[-1]
		m2 = re.match('(\w*)\W*', normalizedParam)

		normalizedParamList.append(m2.group(1))

	normalizedParamList = [s.lower() for s in normalizedParamList]
	normalizedParamList.sort()

	return name + '(' + ', '.join(normalizedParamList) + ')'