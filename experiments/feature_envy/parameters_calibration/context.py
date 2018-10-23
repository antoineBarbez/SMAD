import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, ROOT_DIR)

import utils.entityUtils     as entityUtils
import utils.experimentUtils as experimentUtils
import utils.dataUtils       as dataUtils
import utils.liuUtils        as liuUtils
import utils.nnUtils		 as nnUtils

import detection_tools.feature_envy.hist   as hist
import detection_tools.feature_envy.incode as incode

import experiments.feature_envy.mergedDetection as mergedDetection 

import neural_networks.smad.model as md
import neural_networks.liu_replication.liu_model as liu_model