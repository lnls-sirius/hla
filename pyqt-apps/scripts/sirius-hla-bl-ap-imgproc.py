#!/usr/bin/env python-sirius

"""Image Processing Window."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.bl_ap_imgproc import BLImgProc


parser = argparse.ArgumentParser(
    description="Run Image Processing Window.")
parser.add_argument('dvf', type=str, help='Select a DVF')
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    BLImgProc, parent=None, prefix=args.prefix, dvf=args.dvf)
sys.exit(app.exec_())
