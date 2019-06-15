import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.nnUtils as nnUtils

import approaches.asci.predict  as asci
import approaches.smad.model    as md
import approaches.vote.detect   as vote
import approaches.incode.detect as incode
import approaches.hist.detect_god_class    as hist_gc
import approaches.hist.detect_feature_envy as hist_fe