#!/usr/bin/env python-sirius

"""Open DCCT window of specified section."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_di_dccts import DCCTMain, SISelectDCCT


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('sec', type=str, help='Select a section.')
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

sec = args.sec
prefix = args.prefix

app = SiriusApplication()
if sec == 'BO':
    device = 'BO-35D:DI-DCCT'
    window = DCCTMain(None, prefix=prefix, device=device)
elif sec == 'SI':
    window = SISelectDCCT(None, prefix=prefix)
window.show()
sys.exit(app.exec_())
