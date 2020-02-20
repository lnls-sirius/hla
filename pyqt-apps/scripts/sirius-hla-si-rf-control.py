#!/usr/bin/env python-sirius

"""SI RF Control Window."""

import sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_rf_control.control import RFMainControl


parser = _argparse.ArgumentParser(
    description="Run RF Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(RFMainControl, prefix=args.prefix, section='SI')
sys.exit(app.exec_())
