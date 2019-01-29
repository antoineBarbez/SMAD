from context import incode, experimentUtils, dataUtils

import numpy as np

import progressbar

calibration_systems = [
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant', 
	'apache-tomcat',
	'lucene',
	'argouml',
	'jedit',
	'xerces-2_7_0'
]

# Initialize progressbar
bar = progressbar.ProgressBar(maxval=len(calibration_systems), \
	widgets=['HIST parameters calibration:' ,progressbar.Percentage()])
bar.start()


f_measures = []
for i, system in enumerate(calibration_systems):
	bar.update(i)
	true = dataUtils.getAntipatterns(system, 'feature_envy')
	f_measures.append([[[experimentUtils.f_measure(incode.getSmells(system, atfd, laa, fdp), true) for fdp in range(8)] for laa in range(8)] for atfd in range(8)])

bar.finish()
mean_f_measures = np.mean(f_measures, axis=0)

print('Best values for (atfd, laa, fdp): ' + str(np.unravel_index(np.argmax(mean_f_measures, axis=None), mean_f_measures.shape)))
