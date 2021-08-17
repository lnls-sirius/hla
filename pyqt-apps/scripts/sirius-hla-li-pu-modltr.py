#!/usr/bin/env python-sirius

"""Linac Modulators Control."""
import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.li_pu_modltr import LIModltrWindow


parser = _argparse.ArgumentParser(
    description="Run Linac Modulators Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(LIModltrWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
