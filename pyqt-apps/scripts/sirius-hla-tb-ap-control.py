#!/usr/bin/env python-sirius

"""TB High Level Control Window Application."""

import os
import sys
import argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injcontrol import TLControlWindow
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX


parser = argparse.ArgumentParser(
    description="Run TB Control HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=_VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
app.open_window(
    TLControlWindow, parent=None, prefix=args.prefix, tl='tb')
sys.exit(app.exec_())
