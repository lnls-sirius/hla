#!/usr/bin/env python-sirius

"""Interface to handle general status."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_diag import PSDiag


parser = _argparse.ArgumentParser(
    description="Run Power Supply Diagnosis Interface.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()


app = SiriusApplication()
app.open_window(PSDiag, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
