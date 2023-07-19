#!/usr/bin/env python-sirius

"""Crates Monitor."""

import sys as sys
import argparse as argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_cratemon import CratesMonitor


parser = argparse.ArgumentParser(
    description="Run Crates Monitor.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(CratesMonitor, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
