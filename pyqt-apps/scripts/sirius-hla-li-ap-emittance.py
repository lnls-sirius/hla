#!/usr/bin/env python-sirius

"""Open Window of emittance measurement in Linac."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import vaca_prefix
from siriushla.as_ap_measure import EmittanceMeasure
from siriushla.widgets.windows import create_window_from_widget


parser = _argparse.ArgumentParser(
    description="Run Interface of emittance measurement in Linac.")
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
MyWindow = create_window_from_widget(
    EmittanceMeasure, title='Linac Emittance Measure', is_main=True)
app.open_window(MyWindow, parent=None, place='LI')
sys.exit(app.exec_())
