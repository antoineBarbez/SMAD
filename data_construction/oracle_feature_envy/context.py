import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.entityUtils as entityUtils

import neural_networks.hist.detect_feature_envy       as hist
import neural_networks.incode.detect                  as incode
import neural_networks.jdeodorant.detect_feature_envy as jdeodorant
