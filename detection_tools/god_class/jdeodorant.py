from context import ROOT_DIR

import os


def getSmells(systemName):
	JDBlobFile = os.path.join(ROOT_DIR, 'data/metric_files/jdeodorant/god_class_output/' + systemName + '.txt')
	
	with open(JDBlobFile, 'r') as file:
		return list(set([line.split()[0] for line in file]))
