
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

	directories = "@".join(system['directory'])

	ptidejCommand = "java -jar ../../advisors/detection/Decor/PtidejSmellDetection.jar " + aSmell + " " + directories + " " + system['name'] + " " + cwd + "/../advisors/results/Decor/" + aSmell + "/" + system['name'] + '.csv'

	subprocess.call(ptidejCommand, shell=True)

	subprocess.call('git checkout master', shell=True)
	os.chdir(cwd)

	#removeDirCommand = "rm -rf " + system['name']
	#subprocess.call(removeDirCommand, shell=True)

if __name__ == "__main__":

	'''
	for system in systems.systems_git:
		extractSmellOccurencesWithPtidej(system, "Blob")'''

	#TO ADD
	'''
	roller = {
				"name"     :'apache-roller', 
				"url"      :'https://github.com/apache/roller.git', 
				"snapshot" :'afe6caf', 
				"directory":'src/'}

	'''




