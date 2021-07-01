#!/usr/bin/env python-sirius

"""BO TOCA Application."""

import sys
import argparse as _argparse

import qtawesome as qta
import siriushla.util as util

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ap_sofb import MainWindow
from siriushla.as_ap_sofb.graphics import ShowMatrixWidget
from siriuspy.envars import VACA_PREFIX


parser = _argparse.ArgumentParser(description="Run TOCA HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-m', '--matrix', action='store_true', default=False,
    help="Choose whether to show matrix widget")
args = parser.parse_args()

app = SiriusApplication()
if args.matrix:
    window = create_window_from_widget(
        ShowMatrixWidget, 'Response Matrix',
        icon=qta.icon('fa5s.hammer', color=util.get_appropriate_color('BO')),
        is_main=True)
    app.open_window(
        window, parent=None, prefix=args.prefix + 'BO-Glob:AP-SOFB:', acc='BO')
else:
    app.open_window(MainWindow, parent=None, prefix=args.prefix, acc='BO')
sys.exit(app.exec_())
