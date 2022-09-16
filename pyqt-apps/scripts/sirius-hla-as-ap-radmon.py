#!/usr/bin/env python-sirius

"""RAD Monitor."""

import sys as sys
import argparse as argparse
import qtawesome as qta
from siriushla.util import get_appropriate_color
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_radmon import RadTotDoseMonitor
from siriushla.widgets.windows import create_window_from_widget


parser = argparse.ArgumentParser(
    description="Run RAD Monitor.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
icon = qta.icon('fa5s.radiation', color=get_appropriate_color('AS'))
window = create_window_from_widget(
    RadTotDoseMonitor, 'RAD: Total Dose Monitor',
    is_main=True, withscroll=True, icon=icon)
app.open_window(window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
