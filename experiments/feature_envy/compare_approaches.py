from context import dataUtils, experimentUtils, hist, incode, jdeodorant


# This script is used to compare the performances of various feature envy detection approaches
# on the systems considered in this study.

parameters = {'hist': 2.0, 'incode': (3.0, 3.0, 3.0)}

systems = [
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant', 
	'apache-tomcat',
	'lucene',
	'argouml',
	'jedit',
	'xerces-2_7_0'
]


for system in systems:
	# Get occurrences manually detected on the considered system
	true = dataUtils.getLabels(system, 'feature_envy')


	###   TOOLS   ###

	# Compute performances for HIST
	detected_hist = hist.getSmells(system, parameters['hist'])
	
	precision_hist = experimentUtils.precision(detected_hist, true)
	recall_hist = experimentUtils.recall(detected_hist, true)
	f_measure_hist = experimentUtils.f_measure(detected_hist, true)
	
	# Compute performances for InCode
	detected_incode = incode.getSmells(system, *parameters['incode'])

	precision_incode = experimentUtils.precision(detected_incode, true)
	recall_incode = experimentUtils.recall(detected_incode, true)
	f_measure_incode = experimentUtils.f_measure(detected_incode, true)

	# Compute performances for JDeodorant
	detected_jdeodorant = jdeodorant.getSmells(system)

	precision_jdeodorant = experimentUtils.precision(detected_jdeodorant, true)
	recall_jdeodorant = experimentUtils.recall(detected_jdeodorant, true)
	f_measure_jdeodorant = experimentUtils.f_measure(detected_jdeodorant, true)


	###   VOTE   ###

	tools_outputs = [detected_hist, detected_incode, detected_jdeodorant]

	# Compute vote for k = 1
	detected_vote_1 = experimentUtils.vote(tools_outputs, 1)

	precision_vote_1 = experimentUtils.precision(detected_vote_1, true)
	recall_vote_1 = experimentUtils.recall(detected_vote_1, true)
	f_measure_vote_1 = experimentUtils.f_measure(detected_vote_1, true)

	# Compute vote for k = 2
	detected_vote_2 = experimentUtils.vote(tools_outputs, 2)

	precision_vote_2 = experimentUtils.precision(detected_vote_2, true)
	recall_vote_2 = experimentUtils.recall(detected_vote_2, true)
	f_measure_vote_2 = experimentUtils.f_measure(detected_vote_2, true)

	# Compute vote for k = 3
	detected_vote_3 = experimentUtils.vote(tools_outputs, 3)

	precision_vote_3 = experimentUtils.precision(detected_vote_3, true)
	recall_vote_3 = experimentUtils.recall(detected_vote_3, true)
	f_measure_vote_3 = experimentUtils.f_measure(detected_vote_3, true)

	

	# Output results
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
	print('Vote 2     |' + "{0:.3f}".format(precision_vote_2) + '      |' + "{0:.3f}".format(recall_vote_2) + '   |' + "{0:.3f}".format(f_measure_vote_2))
	print('-------------------------------------------------')
	print('Vote 3     |' + "{0:.3f}".format(precision_vote_3) + '      |' + "{0:.3f}".format(recall_vote_3) + '   |' + "{0:.3f}".format(f_measure_vote_3))
	print('-------------------------------------------------')
	print('\n\n')


