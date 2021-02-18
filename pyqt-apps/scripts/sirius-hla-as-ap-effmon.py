#!/usr/bin/env python-sirius

"""Efficiency Monitor."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ap_currinfo.efficiency_monitor import EfficiencyMonitor


parser = argparse.ArgumentParser(
    description="Run Efficiency Monitor.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(EfficiencyMonitor, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
