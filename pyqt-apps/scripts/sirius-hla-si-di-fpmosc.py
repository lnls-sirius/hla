#!/usr/bin/env python-sirius

"""Open Filling Pattern monitor window."""

import argparse as _argparse
import sys

from siriushla.si_di_fpm_osc import FPMOscMain
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX

parser = _argparse.ArgumentParser(
    description="Run Interface of Filling Pattern Monitor.")
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

prefix = args.prefix

app = SiriusApplication()
window = FPMOscMain(prefix=prefix)
window.show()
sys.exit(app.exec_())
