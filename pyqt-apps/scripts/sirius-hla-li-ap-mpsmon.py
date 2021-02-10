#!/usr/bin/env python-sirius

"""Linac MPS Monitor."""
import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.widgets.windows import create_window_from_widget
from siriushla.li_ap_mps import MPSMonitor


parser = _argparse.ArgumentParser(
    description="Run Linac MPS Monitor Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = create_window_from_widget(
    MPSMonitor, title='LI MPS Monitor', is_main=True,
    withscroll=True, min_width=25)
app.open_window(window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
