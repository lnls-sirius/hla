#!/usr/bin/env python-sirius

"""PS detailed window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pm_control import PulsedMagnetDetailWindow


parser = _argparse.ArgumentParser(
    description="Run Pulsed Magnet Detailed Control Interface.")
parser.add_argument("pmname", type=str, help="PM name.")
args = parser.parse_args()


app = SiriusApplication()
app.open_window(PulsedMagnetDetailWindow, parent=None, maname=args.pmname)
sys.exit(app.exec_())
