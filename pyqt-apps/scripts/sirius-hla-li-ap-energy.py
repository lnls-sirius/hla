#!/usr/bin/env python-sirius

"""Open Window of energy measurement in LI."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_measure import EnergyMeasure
from siriushla.widgets.windows import create_window_from_widget


parser = _argparse.ArgumentParser(
    description="Run Interface of energy measurement in LI.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
MyWindow = create_window_from_widget(
    EnergyMeasure, title='Linac Energy Measure', is_main=True)
app.open_window(MyWindow)
sys.exit(app.exec_())
