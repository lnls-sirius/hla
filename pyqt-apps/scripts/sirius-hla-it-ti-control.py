#!/usr/bin/env python-sirius

"""IT Timing Application."""

import sys as _sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
import qtawesome as qta
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.li_eg_control import ITTIWidget


parser = _argparse.ArgumentParser(
    description="Run IT Timing Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()
prefix = args.prefix + ('-' if args.prefix else '')


app = SiriusApplication()
window = create_window_from_widget(
    ITTIWidget, title='IT Timing Control', icon=qta.icon('mdi.timer'),
    is_main=True)
app.open_window(window, parent=None, prefix=prefix, is_main=True)
_sys.exit(app.exec_())
