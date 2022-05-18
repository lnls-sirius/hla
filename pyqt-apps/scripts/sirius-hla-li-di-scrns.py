#!/usr/bin/env python-sirius

import argparse
import sys

from siriuspy.envars import VACA_PREFIX
from siriushla.li_di_scrns import LiBeamProfile
from siriushla.sirius_application import SiriusApplication

parser = argparse.ArgumentParser(
    description="Run Interface of Beam Profile")
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    LiBeamProfile, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
