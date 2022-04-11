#!/usr/bin/env python-sirius

"""Linac MPS Controller"""
import sys
import argparse as _argparse


from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.li_ap_mps import MPSController

parser = _argparse.ArgumentParser(
    description="Run Linac MPS Controller Interface.")
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    MPSController, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
