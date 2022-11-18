#!/usr/bin/env python-sirius

"""Storage Ring Undulator Control Window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.si_id_control import IDControl, APUControlWindow, \
    EPUControlWindow


parser = _argparse.ArgumentParser(
    description="Run Storage Ring Undulator Control Window.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument(
    '-dev', '--device', type=str, default='',
    help="Define the device.")
parser.add_argument('-isall', action='store_true')
args = parser.parse_args()
prefix = args.prefix
device = args.device
isall = args.isall

app = SiriusApplication()
if 'APU' in args.device:
    app.open_window(
        APUControlWindow, parent=None, prefix=prefix, device=device)
elif 'EPU' in args.device:
    app.open_window(
        EPUControlWindow, parent=None, prefix=prefix, device=device)
elif not device or isall:
    app.open_window(IDControl, parent=None, prefix=prefix)
sys.exit(app.exec_())
