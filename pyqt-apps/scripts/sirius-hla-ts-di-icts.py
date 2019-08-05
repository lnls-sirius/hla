#!/usr/bin/env python-sirius

"""Run interface of ICTs monitoring of specified transport line."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import vaca_prefix
from siriushla.as_di_icts import ICTMonitoring


parser = _argparse.ArgumentParser(
    description="Run interface of ICTs monitoring of specified TL.")
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(ICTMonitoring, parent=None, tl='TS', prefix=args.prefix)
sys.exit(app.exec_())
