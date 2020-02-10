#!/usr/bin/env python-sirius

"""Interface to handle Booster VLight Measure."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_di_vlight import VLightCamView


parser = _argparse.ArgumentParser(
    description="Run Booster VLight Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(VLightCamView, parent=None, prefix=args.prefix, section='BO')
sys.exit(app.exec_())
