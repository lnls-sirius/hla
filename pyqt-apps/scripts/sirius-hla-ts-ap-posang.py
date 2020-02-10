#!/usr/bin/env python-sirius

"""TS Position and Angle Correction Application."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriushla.as_ap_posang.HLPosAng import PosAngCorr


parser = argparse.ArgumentParser(
    description="Run TS PosAng HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=_VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(PosAngCorr, parent=None, prefix=args.prefix, tl='ts')
sys.exit(app.exec_())
