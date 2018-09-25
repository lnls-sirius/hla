#!/usr/bin/env python-sirius

"""High Level Booster Ramp Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.bo_ap_ramp.ramp_main import RampMain
from siriushla import util

parser = _argparse.ArgumentParser(
    description="Run Booster Ramp HLA Interface.")
parser.add_argument('-p', "--prefix", type=str,
                    default='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:',
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
util.set_style(app)
window = RampMain(prefix=args.prefix)
window.show()
sys.exit(app.exec_())
