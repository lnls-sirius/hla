#!/usr/bin/env python-sirius

"""SI FOFB Application."""

import sys
import argparse as _argparse

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.si_ap_fofb import MainWindow, MatrixWidget, get_fofb_icon, \
    ControllersDetailDialog
from siriuspy.envars import VACA_PREFIX


parser = _argparse.ArgumentParser(description="Run FOFB HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-m', '--matrix', action='store_true', default=False,
    help="Choose whether to show matrix widget.")
parser.add_argument(
    '--matrixproperty', type=str, default='RespMat-Mon',
    help="Define which matrix to show.")
parser.add_argument(
    '-d', '--lowleveldetails', action='store_true', default=False,
    help="Choose whether to show low level details window.")

args = parser.parse_args()

app = SiriusApplication()
if args.matrix:
    window = create_window_from_widget(
        MatrixWidget, 'Matrix View', icon=get_fofb_icon(), is_main=True)
    app.open_window(
        window, parent=None, device='SI-Glob:AP-FOFB',
        propty=args.matrixproperty, prefix=args.prefix)
elif args.lowleveldetails:
    app.open_window(
        ControllersDetailDialog, parent=None, device='SI-Glob:AP-FOFB',
        prefix=args.prefix, tab_selected=2)
else:
    app.open_window(
        MainWindow, parent=None, device='SI-Glob:AP-FOFB', prefix=args.prefix)
sys.exit(app.exec_())
