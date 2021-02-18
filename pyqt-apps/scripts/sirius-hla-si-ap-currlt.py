#!/usr/bin/env python-sirius

"""High Level Application to Current and Lifetime Monitoring."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ap_currinfo.current_and_lifetime import CurrLTWindow


parser = argparse.ArgumentParser(
    description="Run Current and Lifetime HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(CurrLTWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
