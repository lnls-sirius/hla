#!/usr/bin/env python-sirius

"""High Level Application to Current and Lifetime Monitoring."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ap_currinfo.charge_monitor import BOMonitor


parser = argparse.ArgumentParser(
    description="Run Booster Charge Monitor HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(BOMonitor, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
