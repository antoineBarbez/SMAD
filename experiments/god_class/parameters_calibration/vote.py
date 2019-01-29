from context import experimentUtils, dataUtils, hist, decor, jdeodorant
from sklearn import tree

import numpy as np

validation_systems = ['xerces-2_7_0', 'lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']

fm_v1 = []
fm_v2 = []
fm_v3 = []
for system in validation_systems:
	antipatterns = dataUtils.getAntipatterns(system, 'god_class')
	detected = [hist.getSmells(system), decor.getSmells(system), jdeodorant.getSmells(system)]

	fm_v1.append(experimentUtils.f_measure(experimentUtils.vote(detected, 1), antipatterns))
	fm_v2.append(experimentUtils.f_measure(experimentUtils.vote(detected, 2), antipatterns))
	fm_v3.append(experimentUtils.f_measure(experimentUtils.vote(detected, 3), antipatterns))

print('V1: ' + str(np.mean(np.array(fm_v1))))
print('V2: ' + str(np.mean(np.array(fm_v2))))
print('V3: ' + str(np.mean(np.array(fm_v3))))