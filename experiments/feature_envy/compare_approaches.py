from context import dataUtils, experimentUtils, hist, incode, jdeodorant

import numpy as np

import smad_fe, asci

# This script is used to compare the performances of:
# - The detection tools aggregated through SMAD
# - The voting technique with k=1
# - ASCI
# - SMAD
# for Feature Envy detection on the three subject systems.

systems = ['android-platform-support', 'apache-tomcat', 'jedit']

p_hist = []
r_hist = []
f_hist = []

p_incode = []
r_incode = []
f_incode = []

p_jd = []
r_jd = []
f_jd = []

p_v1 = []
r_v1 = []
f_v1 = []

p_asci = []
r_asci = []
f_asci = []

p_smad = []
r_smad = []
f_smad = []


for system in systems:
	# Get occurrences manually detected on the considered system
	true = dataUtils.getAntipatterns(system, 'feature_envy')


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
	detected_incode = incode.getSmells(system)

	precision_incode = experimentUtils.precision(detected_incode, true)
	recall_incode = experimentUtils.recall(detected_incode, true)
	f_measure_incode = experimentUtils.f_measure(detected_incode, true)

	p_incode.append(precision_incode)
	r_incode.append(recall_incode)
	f_incode.append(f_measure_incode)

	# Compute performances for JDeodorant
	detected_jdeodorant = jdeodorant.getSmells(system)

	precision_jdeodorant = experimentUtils.precision(detected_jdeodorant, true)
	recall_jdeodorant = experimentUtils.recall(detected_jdeodorant, true)
	f_measure_jdeodorant = experimentUtils.f_measure(detected_jdeodorant, true)

	p_jd.append(precision_jdeodorant)
	r_jd.append(recall_jdeodorant)
	f_jd.append(f_measure_jdeodorant)

	###   VOTE   ###

	tools_outputs = [detected_hist, detected_incode, detected_jdeodorant]

	# Compute vote for k = 1
	detected_vote_1 = experimentUtils.vote(tools_outputs, 1)

	precision_vote_1 = experimentUtils.precision(detected_vote_1, true)
	recall_vote_1 = experimentUtils.recall(detected_vote_1, true)
	f_measure_vote_1 = experimentUtils.f_measure(detected_vote_1, true)

	p_v1.append(precision_vote_1)
	r_v1.append(recall_vote_1)
	f_v1.append(f_measure_vote_1)


	# ASCI
	detected_asci = asci.getSmells(system)

	precision_asci = experimentUtils.precision(detected_asci, true)
	recall_asci = experimentUtils.recall(detected_asci, true)
	f_measure_asci = experimentUtils.f_measure(detected_asci, true)

	p_asci.append(precision_asci)
	r_asci.append(recall_asci)
	f_asci.append(f_measure_asci)


	# SMAD
	detected_smad = smad_fe.getSmells(system)

	precision_smad = experimentUtils.precision(detected_smad, true)
	recall_smad = experimentUtils.recall(detected_smad, true)
	f_measure_smad = experimentUtils.f_measure(detected_smad, true)

	p_smad.append(precision_smad)
	r_smad.append(recall_smad)
	f_smad.append(f_measure_smad)

	# Print performances for the considered system
	print('           |precision  |recall  |f_measure')
	print('-------------------------------------------------')
	print('HIST       |' + "{0:.3f}".format(precision_hist) + '      |' + "{0:.3f}".format(recall_hist) + '   |' + "{0:.3f}".format(f_measure_hist))
	print('-------------------------------------------------')
	print('InCode     |' + "{0:.3f}".format(precision_incode) + '      |' + "{0:.3f}".format(recall_incode) + '   |' + "{0:.3f}".format(f_measure_incode))
	print('-------------------------------------------------')
	print('JDeodorant |' + "{0:.3f}".format(precision_jdeodorant) + '      |' + "{0:.3f}".format(recall_jdeodorant) + '   |' + "{0:.3f}".format(f_measure_jdeodorant))
	print('-------------------------------------------------')
	print('-------------------------------------------------')
	print('Vote 1     |' + "{0:.3f}".format(precision_vote_1) + '      |' + "{0:.3f}".format(recall_vote_1) + '   |' + "{0:.3f}".format(f_measure_vote_1))
	print('-------------------------------------------------')
	print('ASCI       |' + "{0:.3f}".format(precision_asci) + '      |' + "{0:.3f}".format(recall_asci) + '   |' + "{0:.3f}".format(f_measure_asci))
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
print('InCode     |' + "{0:.3f}".format(np.mean(p_incode)) + '      |' + "{0:.3f}".format(np.mean(r_incode)) + '   |' + "{0:.3f}".format(np.mean(f_incode)))
print('-------------------------------------------------')
print('JDeodorant |' + "{0:.3f}".format(np.mean(p_jd)) + '      |' + "{0:.3f}".format(np.mean(r_jd)) + '   |' + "{0:.3f}".format(np.mean(f_jd)))
print('-------------------------------------------------')
print('-------------------------------------------------')
print('Vote 1     |' + "{0:.3f}".format(np.mean(p_v1)) + '      |' + "{0:.3f}".format(np.mean(r_v1)) + '   |' + "{0:.3f}".format(np.mean(f_v1)))
print('-------------------------------------------------')
print('ASCI       |' + "{0:.3f}".format(np.mean(p_asci)) + '      |' + "{0:.3f}".format(np.mean(r_asci)) + '   |' + "{0:.3f}".format(np.mean(f_asci)))
print('-------------------------------------------------')
print('SMAD       |' + "{0:.3f}".format(np.mean(p_smad)) + '      |' + "{0:.3f}".format(np.mean(r_smad)) + '   |' + "{0:.3f}".format(np.mean(f_smad)))
print('-------------------------------------------------')
print('\n\n')