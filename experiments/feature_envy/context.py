import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.dataUtils as dataUtils
import utils.experimentUtils as experimentUtils

import detection_tools.replication.feature_envy.hist       as hist
import detection_tools.replication.feature_envy.incode     as incode
import detection_tools.replication.feature_envy.jdeodorant as jdeodorant