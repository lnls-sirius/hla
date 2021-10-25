#!/usr/bin/env python-sirius

"""Pre Injector Test Area E-gun Control Window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.li_eg_control import LIEgunWindow


parser = _argparse.ArgumentParser(
    description="Run Pre Injector Test Area E-gun Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(LIEgunWindow, parent=None,
                prefix=args.prefix, is_it=True)
sys.exit(app.exec_())
