#!/usr/bin/env python-sirius

"""Open Window of Specified Screen."""

import os
import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import vaca_prefix
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_scrns import SelectScrns


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('sec', type=str, help='Select a section.')
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

sec = args.sec
prefix = args.prefix

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
MyWindow = create_window_from_widget(
    SelectScrns, title='Select a Screen', is_main=True)
app.open_window(MyWindow, parent=None, prefix=prefix, sec=sec)
sys.exit(app.exec_())
