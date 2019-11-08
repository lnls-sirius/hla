#!/usr/bin/env python-sirius

"""High Level Timming Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import vaca_prefix
from siriushla.as_ti_control import TimingMain, SummaryWindow


parser = _argparse.ArgumentParser(description="Run Timing HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-t', "--type", type=str, default='main', choices=('main', 'summary'),
    help="Whether to open summary window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
if args.type.lower() == 'main':
    app.open_window(TimingMain, parent=None, prefix=args.prefix)
else:
    app.open_window(SummaryWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
