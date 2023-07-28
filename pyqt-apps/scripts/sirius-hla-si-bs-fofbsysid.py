#!/usr/bin/env python-sirius

"""High Level Application for FOFB SYSID Acquisitions Control."""

import sys as _sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_fofb import FOFBAcqSYSIDWindow


parser = _argparse.ArgumentParser(
    description="Run FOFBCtrl SYSID acquisitions interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument('device', type=str, help='Select a device.')
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    FOFBAcqSYSIDWindow, parent=None,
    prefix=args.prefix, device=args.device)
_sys.exit(app.exec_())
