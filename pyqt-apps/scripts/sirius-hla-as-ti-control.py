#!/usr/bin/env python-sirius

"""High Level Timming Application."""

import sys
import argparse as _argparse

from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import TimingMain, MonitorWindow
from siriushla.util import get_appropriate_color, get_monitor_icon

parser = _argparse.ArgumentParser(description="Run Timing HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-t', "--type", type=str, default='main', choices=('main', 'monitor'),
    help="Whether to open monitor window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
if args.type.lower() == 'main':
    app.open_window(TimingMain, parent=None, prefix=args.prefix)
else:
    icon = get_monitor_icon('mdi.timer', color=get_appropriate_color('AS'))
    window = create_window_from_widget(
        MonitorWindow, title='Timing Monitor', icon=icon,
        is_main=True, withscroll=True, min_width=25)
    app.open_window(window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
