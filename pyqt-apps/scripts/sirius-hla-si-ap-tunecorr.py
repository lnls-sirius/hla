#!/usr/bin/env python-sirius
"""High Level Application to Storage Ring Tune Correction."""

import sys as _sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_opticscorr import OpticsCorrWindow


parser = _argparse.ArgumentParser(
    description="Run Storage Ring Tune Correction HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    OpticsCorrWindow, parent=None, acc='si', opticsparam='tune',
    prefix=args.prefix)
_sys.exit(app.exec_())
