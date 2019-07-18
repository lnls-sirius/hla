#!/usr/bin/env python-sirius

"""TB High Level Control Window Application."""

import os
import sys
import argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.tl_ap_control.HLTLControl import TLAPControlWindow
from siriuspy.envars import vaca_prefix as _vaca_prefix


parser = argparse.ArgumentParser(
    description="Run TB Control HLA Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=_vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
app.open_window(
    TLAPControlWindow, parent=None, prefix=args.prefix, tl='tb')
sys.exit(app.exec_())
