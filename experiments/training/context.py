import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.dataUtils as dataUtils
import utils.nnUtils as nnUtils

import neural_networks.smad.model as md