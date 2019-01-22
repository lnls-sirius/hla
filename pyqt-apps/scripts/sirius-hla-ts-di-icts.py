#!/usr/bin/env python-sirius

"""Run interface of ICTs monitoring of specified transport line."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.tl_ap_control import ICTMonitoring


parser = _argparse.ArgumentParser(
    description="Run interface of ICTs monitoring of specified transport line")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
w = ICTMonitoring(tl='TS', prefix=args.prefix)
w.show()
sys.exit(app.exec_())
