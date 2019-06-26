#!/usr/bin/env python-sirius

"""High Level Booster Ramp Application."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.bo_ap_ramp.main_window import RampMain

parser = _argparse.ArgumentParser(
    description="Run Booster Ramp HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
app.open_window(RampMain, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
