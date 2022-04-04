#!/usr/bin/env python-sirius

"""Injection Application."""

import sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injection import InjCtrlWindow


parser = _argparse.ArgumentParser(
    description="Run Operation Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
app.open_window(InjCtrlWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
