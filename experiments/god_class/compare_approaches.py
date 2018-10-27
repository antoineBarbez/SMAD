from context import dataUtils, experimentUtils, hist, decor, jdeodorant

import numpy as np

import smad_gc

# This script is used to compare the performances of:
# - The detection tools aggregated through SMAD
# - The voting technique with k in {1, 2, 3}
# - SMAD
# for God Class detection on the three subject systems.

systems = ['apache-tomcat', 'jedit', 'android-platform-support']

p_hist = []
r_hist = []
f_hist = []

p_decor = []
r_decor = []
f_decor = []

p_jd = []
r_jd = []
f_jd = []

p_v1 = []
r_v1 = []
f_v1 = []

p_v2 = []
r_v2 = []
f_v2 = []

p_v3 = []
r_v3 = []
f_v3 = []

p_smad = []
r_smad = []
f_smad = []
for system in systems:
	# Get occurrences manually detected on the considered system
	true = dataUtils.getAntipatterns(system, 'god_class')

	###   TOOLS   ###

	# Compute performances for HIST
	detected_hist = hist.getSmells(system)
	
	precision_hist = experimentUtils.precision(detected_hist, true)
	recall_hist = experimentUtils.recall(detected_hist, true)
	f_measure_hist = experimentUtils.f_measure(detected_hist, true)

	p_hist.append(precision_hist)
	r_hist.append(recall_hist)
	f_hist.append(f_measure_hist)
	
	# Compute performances for InCode
	detected_decor = decor.getSmells(system)

	precision_decor = experimentUtils.precision(detected_decor, true)
	recall_decor = experimentUtils.recall(detected_decor, true)
	f_measure_decor = experimentUtils.f_measure(detected_decor, true)

	p_decor.append(precision_decor)
	r_decor.append(recall_decor)
	f_decor.append(f_measure_decor)

	# Compute performances for JDeodorant
	detected_jdeodorant = jdeodorant.getSmells(system)

	precision_jdeodorant = experimentUtils.precision(detected_jdeodorant, true)
	recall_jdeodorant = experimentUtils.recall(detected_jdeodorant, true)
	f_measure_jdeodorant = experimentUtils.f_measure(detected_jdeodorant, true)

	p_jd.append(precision_jdeodorant)
	r_jd.append(recall_jdeodorant)
	f_jd.append(f_measure_jdeodorant)

	###   VOTE   ###

	tools_outputs = [detected_hist, detected_decor, detected_jdeodorant]

	# Compute vote for k = 1
	detected_vote_1 = experimentUtils.vote(tools_outputs, 1)

	precision_vote_1 = experimentUtils.precision(detected_vote_1, true)
	recall_vote_1 = experimentUtils.recall(detected_vote_1, true)
	f_measure_vote_1 = experimentUtils.f_measure(detected_vote_1, true)

	p_v1.append(precision_vote_1)
	r_v1.append(recall_vote_1)
	f_v1.append(f_measure_vote_1)

	# Compute vote for k = 2
	detected_vote_2 = experimentUtils.vote(tools_outputs, 2)

	precision_vote_2 = experimentUtils.precision(detected_vote_2, true)
	recall_vote_2 = experimentUtils.recall(detected_vote_2, true)
	f_measure_vote_2 = experimentUtils.f_measure(detected_vote_2, true)

	p_v2.append(precision_vote_2)
	r_v2.append(recall_vote_2)
	f_v2.append(f_measure_vote_2)

	# Compute vote for k = 3
	detected_vote_3 = experimentUtils.vote(tools_outputs, 3)

	precision_vote_3 = experimentUtils.precision(detected_vote_3, true)
	recall_vote_3 = experimentUtils.recall(detected_vote_3, true)
	f_measure_vote_3 = experimentUtils.f_measure(detected_vote_3, true)

	p_v3.append(precision_vote_3)
	r_v3.append(recall_vote_3)
	f_v3.append(f_measure_vote_3)

	# SMAD
	detected_smad = smad_gc.getSmells(system)

	precision_smad = experimentUtils.precision(detected_smad, true)
	recall_smad = experimentUtils.recall(detected_smad, true)
	f_measure_smad = experimentUtils.f_measure(detected_smad, true)

	p_smad.append(precision_smad)
	r_smad.append(recall_smad)
	f_smad.append(f_measure_smad)


	# Print performances for the considered system
	print(system)
	print('           |precision  |recall  |f_measure')
	print('-------------------------------------------------')
	print('HIST       |' + "{0:.3f}".format(precision_hist) + '      |' + "{0:.3f}".format(recall_hist) + '   |' + "{0:.3f}".format(f_measure_hist))
	print('-------------------------------------------------')
	print('DECOR      |' + "{0:.3f}".format(precision_decor) + '      |' + "{0:.3f}".format(recall_decor) + '   |' + "{0:.3f}".format(f_measure_decor))
	print('-------------------------------------------------')
	print('JDeodorant |' + "{0:.3f}".format(precision_jdeodorant) + '      |' + "{0:.3f}".format(recall_jdeodorant) + '   |' + "{0:.3f}".format(f_measure_jdeodorant))
	print('-------------------------------------------------')
	print('-------------------------------------------------')
	print('Vote 1     |' + "{0:.3f}".format(precision_vote_1) + '      |' + "{0:.3f}".format(recall_vote_1) + '   |' + "{0:.3f}".format(f_measure_vote_1))
	print('-------------------------------------------------')
	print('Vote 2     |' + "{0:.3f}".format(precision_vote_2) + '      |' + "{0:.3f}".format(recall_vote_2) + '   |' + "{0:.3f}".format(f_measure_vote_2))
	print('-------------------------------------------------')
	print('Vote 3     |' + "{0:.3f}".format(precision_vote_3) + '      |' + "{0:.3f}".format(recall_vote_3) + '   |' + "{0:.3f}".format(f_measure_vote_3))
	print('-------------------------------------------------')
	print('SMAD       |' + "{0:.3f}".format(precision_smad) + '      |' + "{0:.3f}".format(recall_smad) + '   |' + "{0:.3f}".format(f_measure_smad))
	print('-------------------------------------------------')
	print('\n\n')


# Print average performances over the three systems
print('MEAN')
print('           |precision  |recall  |f_measure')
print('-------------------------------------------------')
print('HIST       |' + "{0:.3f}".format(np.mean(p_hist)) + '      |' + "{0:.3f}".format(np.mean(r_hist)) + '   |' + "{0:.3f}".format(np.mean(f_hist)))
print('-------------------------------------------------')
print('DECOR      |' + "{0:.3f}".format(np.mean(p_decor)) + '      |' + "{0:.3f}".format(np.mean(r_decor)) + '   |' + "{0:.3f}".format(np.mean(f_decor)))
print('-------------------------------------------------')
print('JDeodorant |' + "{0:.3f}".format(np.mean(p_jd)) + '      |' + "{0:.3f}".format(np.mean(r_jd)) + '   |' + "{0:.3f}".format(np.mean(f_jd)))
print('-------------------------------------------------')
print('-------------------------------------------------')
print('Vote 1     |' + "{0:.3f}".format(np.mean(p_v1)) + '      |' + "{0:.3f}".format(np.mean(r_v1)) + '   |' + "{0:.3f}".format(np.mean(f_v1)))
print('-------------------------------------------------')
print('Vote 2     |' + "{0:.3f}".format(np.mean(p_v2)) + '      |' + "{0:.3f}".format(np.mean(r_v2)) + '   |' + "{0:.3f}".format(np.mean(f_v2)))
print('-------------------------------------------------')
print('Vote 3     |' + "{0:.3f}".format(np.mean(p_v3)) + '      |' + "{0:.3f}".format(np.mean(r_v3)) + '   |' + "{0:.3f}".format(np.mean(f_v3)))
print('-------------------------------------------------')
print('SMAD       |' + "{0:.3f}".format(np.mean(p_smad)) + '      |' + "{0:.3f}".format(np.mean(r_smad)) + '   |' + "{0:.3f}".format(np.mean(f_smad)))
print('-------------------------------------------------')
print('\n\n')