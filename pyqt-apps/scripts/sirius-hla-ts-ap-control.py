#!/usr/bin/env python-sirius

"""TS High Level Control Window Application."""

import os
import sys
import argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.envars import vaca_prefix
    from siriushla.tl_ap_control.HLTLControl import TLAPControlWindow

    parser = argparse.ArgumentParser(
                        description="Run TS Control HLA Interface.")
    parser.add_argument(
        '-p', "--prefix", type=str, default=vaca_prefix,
        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()

    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
    app = SiriusApplication()
    app.open_window(
        TLAPControlWindow, parent=None, prefix=args.prefix, tl='ts')
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
