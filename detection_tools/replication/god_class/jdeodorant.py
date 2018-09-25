from context import ROOT_DIR

import os


def getSmells(systemName):
	JDBlobFile = os.path.join(ROOT_DIR, 'detection_tools/metrics_files/god_class/jdeodorant/' + systemName + '.txt')
	
	with open(JDBlobFile, 'r') as file:
		return list(set([line.split()[0] for line in file]))
