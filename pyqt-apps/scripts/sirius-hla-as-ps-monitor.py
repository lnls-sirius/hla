#!/usr/bin/env python-sirius

"""PS Monitor."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ps_diag import PSMonitor
from siriushla.widgets.windows import create_window_from_widget

parser = _argparse.ArgumentParser(
    description="Run PS Monitor Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = create_window_from_widget(
    PSMonitor, title='PS & PU Monitor', is_main=True, withscroll=True)
app.open_window(window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
