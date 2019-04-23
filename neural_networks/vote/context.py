import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import detection_tools.god_class.hist       as hist_gc
import detection_tools.god_class.decor      as decor_gc
import detection_tools.god_class.jdeodorant as jdeodorant_gc

import detection_tools.feature_envy.hist       as hist_fe
import detection_tools.feature_envy.incode     as incode_fe
import detection_tools.feature_envy.jdeodorant as jdeodorant_fe

import utils.dataUtils as dataUtils