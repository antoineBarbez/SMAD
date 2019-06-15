import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.entityUtils as entityUtils

import approaches.hist.detect_feature_envy       as hist
import approaches.incode.detect                  as incode
import approaches.jdeodorant.detect_feature_envy as jdeodorant
