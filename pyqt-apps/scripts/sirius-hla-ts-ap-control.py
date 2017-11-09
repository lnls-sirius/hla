#!/usr/bin/env python-sirius

"""TS High Level Control Window Application."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.tl_ap_control.HLTLControl import TLAPControlWindow
from siriushla import util


parser = argparse.ArgumentParser(
                    description="Run TS Control HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default='',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
util.set_style(app)
window = TLAPControlWindow(prefix=args.prefix, tl='ts')
window.show()
sys.exit(app.exec_())
