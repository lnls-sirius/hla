#!/usr/bin/env python-sirius


import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import vaca_prefix
from siriushla.as_ap_injcontrol import InjBOControlWindow


parser = _argparse.ArgumentParser(description="Run InjBO HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(InjBOControlWindow, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
