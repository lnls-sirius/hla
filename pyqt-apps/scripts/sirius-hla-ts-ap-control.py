#!/usr/bin/env python-sirius

"""TS High Level Control Window Application."""

import os
import sys
import argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injcontrol import TLControlWindow
from siriuspy.envars import vaca_prefix as _vaca_prefix


parser = argparse.ArgumentParser(
    description="Run TS Control HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=_vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
app.open_window(
    TLControlWindow, parent=None, prefix=args.prefix, tl='ts')
sys.exit(app.exec_())
