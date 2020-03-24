#!/usr/bin/env python-sirius

"""Open Window to control SI Scrapers widgets."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.si_di_scraps import ScrapersView
from siriushla.widgets.windows import create_window_from_widget


parser = _argparse.ArgumentParser(
    description="Run Interface to control SI Scrapers widgets.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
prefix = args.prefix
window = create_window_from_widget(
    ScrapersView, title='SI Scrapers View', is_main=True)
app.open_window(window, parent=None, prefix=prefix)
sys.exit(app.exec_())
