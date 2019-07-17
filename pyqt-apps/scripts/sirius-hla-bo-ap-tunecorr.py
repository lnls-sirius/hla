#!/usr/bin/env python-sirius
"""High Level Application to Booster Tune Correction."""

import sys as _sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.envars import vaca_prefix
    from siriushla.as_ap_opticscorr.HLOpticsCorr import OpticsCorrWindow

    parser = _argparse.ArgumentParser(
        description="Run Booster Tune Correction HLA Interface.")
    parser.add_argument(
        '-p', "--prefix", type=str, default=vaca_prefix,
        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = SiriusApplication()
    app.open_window(
        OpticsCorrWindow, parent=None, acc='bo', opticsparam='tune',
        prefix=args.prefix)
    _sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
