#!/usr/bin/env python-sirius

"""Linac MPS Controller"""
import sys
import argparse as _argparse


from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.li_ap_mps import MPSControl

parser = _argparse.ArgumentParser(
    description="Run Linac MPS Control Interface.")
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = create_window_from_widget(
    MPSControl, title='LI MPS Control', is_main=True,
    withscroll=True, min_width=67)
app.open_window(
    window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
