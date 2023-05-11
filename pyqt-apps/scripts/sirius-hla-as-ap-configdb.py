#!/usr/bin/env python-sirius

"""Lauch configuration database manager."""
import sys

import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.as_ap_configdb import ConfigurationManager

parser = _argparse.ArgumentParser(
    description="Run ConfigDB Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-x', '--xpos', type=int, default=0,
    help="Define left origin point of window")
parser.add_argument(
    '-y', '--ypos', type=int, default=20,
    help="Define top origin point of window")
parser.add_argument(
    '-wi', '--width', type=int, default=0,
    help="Define window width value")
parser.add_argument(
    '-he', '--height', type=int, default=0,
    help="Define window height value")
args = parser.parse_args()


app = SiriusApplication()
model = ConfigDBClient()
app.open_window(ConfigurationManager, parent=None, model=model, args=args)
sys.exit(app.exec_())
