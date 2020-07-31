#!/usr/bin/env python-sirius

"""Open Window of beam line MVS2."""

import os
import sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriuspy.meas.manaca.csdev import Const
from siriushla.sirius_application import SiriusApplication
from siriushla.bl_ap_analysis import BeamLineMVS2View


os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '6000000'  # image is large
os.environ['EPICS_CA_ADDR_LIST'] += ' ' + Const.IP_IOC

parser = _argparse.ArgumentParser(
    description="Run Interface of beam line MVS2.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")

args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    BeamLineMVS2View, parent=None, prefix=args.prefix,
    device_analysis=Const.PREFIX_IOC, device_cam=Const.DEF_PROFILE)
sys.exit(app.exec_())
