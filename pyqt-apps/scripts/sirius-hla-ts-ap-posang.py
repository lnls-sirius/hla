#!/usr/bin/env python-sirius

"""TS Position and Angle Correction Application."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.envars import vaca_prefix as _vaca_prefix
    from siriushla.as_ap_posang.HLPosAng import ASAPPosAngCorr

    parser = argparse.ArgumentParser(
                        description="Run TS PosAng HLA Interface.")
    parser.add_argument(
        '-p', "--prefix", type=str, default=_vaca_prefix,
        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = SiriusApplication()
    app.open_window(ASAPPosAngCorr, parent=None, prefix=args.prefix, tl='ts')
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
