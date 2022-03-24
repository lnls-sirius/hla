#!/usr/bin/env python-sirius

import argparse
import sys

from siriuspy.envars import VACA_PREFIX
from siriushla.li_di_bpms import DigBeamPosProc
from siriushla.sirius_application import SiriusApplication

parser = argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument('device', type=str, help='Select a device.')
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    DigBeamPosProc, parent=None, device_name=args.device, prefix=args.prefix)
sys.exit(app.exec_())
