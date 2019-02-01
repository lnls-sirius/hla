#!/usr/bin/env python-sirius

"""High Level Timming Application."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ti_control import TimingMain


parser = _argparse.ArgumentParser(description="Run Timing HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
window = TimingMain(prefix=args.prefix)
window.show()

sys.exit(app.exec_())
