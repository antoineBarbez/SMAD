import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import approaches.decor.detect                as decor
import approaches.hist.detect_god_class       as hist_gc
import approaches.jdeodorant.detect_god_class as jdeodorant_gc

import approaches.incode.detect                  as incode
import approaches.hist.detect_feature_envy       as hist_fe
import approaches.jdeodorant.detect_feature_envy as jdeodorant_fe

import utils.nnUtils as nnUtils