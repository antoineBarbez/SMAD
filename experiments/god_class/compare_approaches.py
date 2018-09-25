from context import dataUtils, experimentUtils, hist, decor, jdeodorant


# This script is used to compare the performances of various god class detection approaches
# on the systems considered in this study.

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
	true = dataUtils.getAntipatterns(system, 'god_class')


	###   TOOLS   ###

	# Compute performances for HIST
	detected_hist = hist.getSmells(system)
	
	precision_hist = experimentUtils.precision(detected_hist, true)
	recall_hist = experimentUtils.recall(detected_hist, true)
	f_measure_hist = experimentUtils.f_measure(detected_hist, true)
	
	# Compute performances for InCode
	detected_decor = decor.getSmells(system)

	precision_decor = experimentUtils.precision(detected_decor, true)
	recall_decor = experimentUtils.recall(detected_decor, true)
	f_measure_decor = experimentUtils.f_measure(detected_decor, true)

	# Compute performances for JDeodorant
	detected_jdeodorant = jdeodorant.getSmells(system)

	precision_jdeodorant = experimentUtils.precision(detected_jdeodorant, true)
	recall_jdeodorant = experimentUtils.recall(detected_jdeodorant, true)
	f_measure_jdeodorant = experimentUtils.f_measure(detected_jdeodorant, true)


	###   VOTE   ###

	tools_outputs = [detected_hist, detected_decor, detected_jdeodorant]

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
	print('\n\n')