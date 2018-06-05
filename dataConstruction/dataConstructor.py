
import systems
import subprocess
import os



# This method is used to create the metrics files necessary to compute Decor ant InCode confidence metrics 
def createMetricsFile(smell, system):
	if smell == "GC":
		smellDir = "god_class/Decor"
		jarFile = "../advisors/metrics_files_generators/Decor/GodClassMetricsFileCreator.jar"
	elif smell == "FE":
		smellDir = "feature_envy/InCode"
		jarFile = "../advisors/metrics_files_generators/InCode/FeatureEnvyMetricsFileCreator.jar"
	else:
		print(smell + " is not a valid smell")
		return

	cloneCommand = 'git clone ' + system['url'] + ' ' + system['name']
	subprocess.call(cloneCommand, shell=True)

	cwd = os.getcwd()
	os.chdir(system['name'])
	subprocess.call('git checkout -f '+ system['snapshot'], shell=True)
	os.chdir(cwd)

	name = system['name']
	repositoryPath = cwd + "/" + name + "/"
	directories = "@".join(system['directory'])
	metricsFile = cwd + "/../advisors/metrics_files/"+ smellDir + "/" + name + '.csv'

	createCommand = "java -jar " + jarFile + " " + name + " " + repositoryPath + " " + directories + " " + metricsFile

	subprocess.call(createCommand, shell=True)

	removeDirCommand = "rm -rf " + system['name']
	subprocess.call(removeDirCommand, shell=True)


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

	'''s = {
	"name"     :'apache-velocity',
	"url"      :'https://github.com/apache/velocity-engine.git',
	"snapshot" :'23c979d3b185ace79c06fc7bedfcc1b9c232eb06',
	"directory":['src/']
	}

	extractSmellOccurencesWithPtidej(s, "Blob")'''

	s = {
	"name"     :'jedit',
	"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
	"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
	"directory":['']
	}

	
	createMetricsFile("FE", s)




