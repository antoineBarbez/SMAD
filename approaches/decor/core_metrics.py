from context import ROOT_DIR

import utils.data_utils as data_utils

import csv
import os

def getGCCoreMetrics(systemName):
	decorMetricsFile = os.path.join(ROOT_DIR, 'approaches', 'decor', 'metric_files', systemName + '.csv')

	dictionnary = {c:[0., 0., 0, 0] for c in data_utils.getClasses(systemName)}
	with open(decorMetricsFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		for row in reader:
			nmdnad = float(row['NMD+NAD'])/float(row['nmdNadBound'])
			lcom = float(row['LCOM5'])/float(row['lcom5Bound'])
			cc = int(row['ControllerClass'])
			dataClass = int(row['nbDataClass'])

			className = row['ClassName']
			if className in dictionnary:
				dictionnary[className] = [nmdnad, lcom, cc, dataClass]

	return dictionnary