#!/usr/bin/env python-sirius

"""Sirius Monitor."""

import sys
import argparse as _argparse

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX
from siriushla.util import get_appropriate_color
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_monitor import SiriusMonitor
from siriushla.widgets.windows import create_window_from_widget


parser = _argparse.ArgumentParser(
    description="Run Sirius Monitor Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
color = get_appropriate_color(section='AS')
icon = qta.icon('mdi.monitor-dashboard', color=color)
window = create_window_from_widget(
    SiriusMonitor, title='Sirius Monitor', icon=icon,
    is_main=True, withscroll=True, min_width=96)
app.open_window(window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
