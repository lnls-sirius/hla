#!/usr/bin/env python-sirius

"""High Level Application for ID feedforward Monitoring."""

import sys as _sys
import argparse as _argparse
from siriuspy.envars import VACA_PREFIX
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_idff.main import IDFFWindow


parser = _argparse.ArgumentParser(
    description="Run ID feedforward Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument("idname", type=str, help="ID name.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    IDFFWindow, parent=None, prefix=args.prefix, idname=args.idname)
_sys.exit(app.exec_())
