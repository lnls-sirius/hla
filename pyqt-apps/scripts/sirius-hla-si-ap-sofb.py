#!/usr/bin/env python-sirius

"""SI SOFB Application."""

import sys
import argparse as _argparse
from pydm import PyDMApplication
from siriushla.si_ap_sofb import main
from siriushla import util


parser = _argparse.ArgumentParser(description="Run SOFB HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default='',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = main(args.prefix)
window.show()
sys.exit(app.exec_())
