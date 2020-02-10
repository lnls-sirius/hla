#!/usr/bin/env python-sirius

"""Open DCCT window of specified section."""

import sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.as_di_dccts import DCCTMain


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('dev', type=str, help='Select a device.')
parser.add_argument('-p', "--prefix", type=str, default=VACA_PREFIX,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

dev = args.dev
prefix = args.prefix

app = SiriusApplication()
window = DCCTMain(None, prefix=prefix, device=dev)
window.show()
sys.exit(app.exec_())
