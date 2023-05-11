#!/usr/bin/env python-sirius

"""Interface to handle Booster Tune Measure."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_di_tune import Tune


parser = _argparse.ArgumentParser(
    description="Run Storage Ring Tune Interface.")
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
parser.add_argument(
    '--expand1', default=True, action='store_true',
    help="Expand pointer 1")
parser.add_argument(
    '--no-expand1', dest='expand1', action='store_false',
    help="Do not expand pointer 1")
parser.add_argument(
    '--expand2', default=True, action='store_true',
    help="Expand pointer 2")
parser.add_argument(
    '--no-expand2', dest='expand2', action='store_false',
    help="Do not expand pointer 2")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(Tune, parent=None, prefix=args.prefix, section='SI', args=args)
sys.exit(app.exec_())
