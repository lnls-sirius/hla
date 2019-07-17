#!/usr/bin/env python-sirius

"""SI SOFB Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_ap_sofb import MainWindow
    from siriuspy.envars import vaca_prefix

    parser = _argparse.ArgumentParser(description="Run SOFB HLA Interface.")
    parser.add_argument(
        '-p', "--prefix", type=str, default=vaca_prefix,
        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    app = SiriusApplication()
    app.open_window(MainWindow, parent=None, prefix=args.prefix)
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
