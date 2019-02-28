#!/usr/bin/env python-sirius

"""TS Position and Angle Correction Application."""

import sys as sys
import argparse as argparse
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_posang.HLPosAng import ASAPPosAngCorr


parser = argparse.ArgumentParser(
                    description="Run TS PosAng HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default=_vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = ASAPPosAngCorr(prefix=args.prefix, tl='ts')
window.show()
sys.exit(app.exec_())
