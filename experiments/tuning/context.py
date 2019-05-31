import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.nnUtils as nnUtils

import neural_networks.asci.predict  as asci
import neural_networks.smad.model    as md
import neural_networks.vote.detect   as vote
import neural_networks.incode.detect as incode
import neural_networks.hist.detect_god_class    as hist_gc
import neural_networks.hist.detect_feature_envy as hist_fe