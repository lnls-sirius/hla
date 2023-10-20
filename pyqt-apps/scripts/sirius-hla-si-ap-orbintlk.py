#!/usr/bin/env python-sirius

"""BPM Orbit Interlock Control Interface."""

import sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_orbintlk import BPMOrbIntlkMainWindow


parser = _argparse.ArgumentParser(
    description="Run Linac MPS Monitor Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(BPMOrbIntlkMainWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
