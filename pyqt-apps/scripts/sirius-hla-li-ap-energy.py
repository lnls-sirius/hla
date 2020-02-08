#!/usr/bin/env python-sirius

"""Open Window of energy measurement in LI."""

import os
import sys
import argparse as _argparse
import qtawesome as qta
from siriuspy.envars import VACA_PREFIX
import siriushla.util as _util
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_measure import EnergyMeasure
from siriushla.widgets.windows import create_window_from_widget


# Linac image is very large! (2448 X 2050)
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '21000000'

parser = _argparse.ArgumentParser(
    description="Run Interface of energy measurement in LI.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
icon = qta.icon(
        'mdi.gauge', color=_util.get_appropriate_color('LI'))
MyWindow = create_window_from_widget(
    EnergyMeasure, title='Linac Energy Measure', is_main=True, icon=icon)
app.open_window(MyWindow)
sys.exit(app.exec_())
