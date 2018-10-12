#!/usr/bin/env python-sirius

"""SI SOFB Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_sofb import MainWindow
from siriushla import util


parser = _argparse.ArgumentParser(description="Run SOFB HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default='',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
util.set_style(app)
window = MainWindow(args.prefix, acc='BO')
window.show()
sys.exit(app.exec_())
