from context import hist, experimentUtils, dataUtils

import numpy             as np
import matplotlib.pyplot as plt

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

alpha_values = np.arange(0.0, 20.0, 0.5)

f_measures = []
for i, system in enumerate(calibration_systems):
	bar.update(i)
	true = dataUtils.getAntipatterns(system, 'god_class')
	f_measures.append([experimentUtils.f_measure(hist.getSmells(system, alpha), true) for alpha in alpha_values])

bar.finish()
mean_f_measures = np.mean(f_measures, axis=0)

print('Best alpha: ' + str(alpha_values[np.argmax(mean_f_measures)]))

plt.plot(alpha_values, mean_f_measures)
plt.show()

