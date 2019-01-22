#!/usr/bin/env python-sirius

"""High Level Timming Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ti_control import main


parser = _argparse.ArgumentParser(description="Run Timing HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default='',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
window = main(args.prefix)
window.show()
sys.exit(app.exec_())
