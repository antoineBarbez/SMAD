
import systems
import subprocess
import os



'''
	All the code and methods used to extract and construct data
'''

def extractSmellOccurencesWithPtidej(system, aSmell):
	cloneCommand = 'git clone ' + system['url'] + ' ' + system['name']
	subprocess.call(cloneCommand, shell=True)

	cwd = os.getcwd()
	os.chdir(system['name'])
	subprocess.call('git checkout -f '+ system['snapshot'], shell=True)

	ptidejCommand = "java -jar ../../assets/frameworks/PtidejSmellDetection.jar " + aSmell + " ./" + system['directory'] + " " + system['name'] + " " + cwd + "/../data/advisors-detection-results/Ptidej/" + aSmell + "/" + system['name'] + '.csv'

	subprocess.call(ptidejCommand, shell=True)

	subprocess.call('git checkout master', shell=True)
	os.chdir(cwd)

	removeDirCommand = "rm -rf " + system['name']
	subprocess.call(removeDirCommand, shell=True)

if __name__ == "__main__":
	'''
	For jedit you must first use the command git svn before extracting smells
	jedit = {
				"name"     :'jedit',
				"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
				"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
				"directory":''}


	extractSmellOccurencesWithPtidej(jedit, "Blob")

	for system in systems.systems:
		extractSmellOccurencesWithPtidej(system, "Blob")'''


	'''ant = {
		"name"     :'apache-ant', 
		"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
		"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
		"directory":'src/main/'}

	extractSmellOccurencesWithPtidej(ant, "Blob")'''

