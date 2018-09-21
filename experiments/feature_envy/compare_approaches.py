from context import dataUtils, evaluate, hist, incode, jdeodorant


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

	# Compute performances for HIST
	detected_hist = hist.getSmells(system, parameters['hist'])
	
	precision_hist = evaluate.precision(detected_hist, true)
	recall_hist = evaluate.recall(detected_hist, true)
	f_measure_hist = evaluate.f_measure(detected_hist, true)
	
	# Compute performances for InCode
	detected_incode = incode.getSmells(system, *parameters['incode'])

	precision_incode = evaluate.precision(detected_incode, true)
	recall_incode = evaluate.recall(detected_incode, true)
	f_measure_incode = evaluate.f_measure(detected_incode, true)

	# Compute performances for JDeodorant
	detected_jdeodorant = jdeodorant.getSmells(system)

	precision_jdeodorant = evaluate.precision(detected_jdeodorant, true)
	recall_jdeodorant = evaluate.recall(detected_jdeodorant, true)
	f_measure_jdeodorant = evaluate.f_measure(detected_jdeodorant, true)
	

	# Output results
	print('           |precision  |recall  |f_measure')
	print('-------------------------------------------------')
	print('HIST       |' + "{0:.3f}".format(precision_hist) + '      |' + "{0:.3f}".format(recall_hist) + '   |' + "{0:.3f}".format(f_measure_hist))
	print('-------------------------------------------------')
	print('InCode     |' + "{0:.3f}".format(precision_incode) + '      |' + "{0:.3f}".format(recall_incode) + '   |' + "{0:.3f}".format(f_measure_incode))
	print('-------------------------------------------------')
	print('JDeodorant |' + "{0:.3f}".format(precision_jdeodorant) + '      |' + "{0:.3f}".format(recall_jdeodorant) + '   |' + "{0:.3f}".format(f_measure_jdeodorant))
	print('\n\n')


