#!/usr/bin/env python-sirius

"""Open Window of Specified Screen."""

import os
import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_di_scrns import SelectScrns


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('sec', type=str, help='Select a section.')
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

sec = args.sec
prefix = args.prefix

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
window = SelectScrns(None, prefix=prefix, sec=sec)
window.setWindowTitle('Select a Screen')
window.show()
sys.exit(app.exec_())
