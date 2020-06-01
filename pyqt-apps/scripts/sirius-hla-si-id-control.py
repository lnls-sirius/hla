#!/usr/bin/env python-sirius

"""Storage Ring Undulator Control Window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.si_id_control import APUControlWindow


parser = _argparse.ArgumentParser(
    description="Run Storage Ring Undulator Control Window.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument('-dev', '--device', type=str, default='')
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    APUControlWindow, parent=None, prefix=args.prefix, device=args.device)
sys.exit(app.exec_())
