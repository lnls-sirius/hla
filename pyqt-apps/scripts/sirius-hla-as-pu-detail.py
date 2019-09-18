#!/usr/bin/env python-sirius

"""PS detailed window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUDetailWindow


parser = _argparse.ArgumentParser(
    description="Run Pulsed Magnet Detailed Control Interface.")
parser.add_argument("pmname", type=str, help="Pulsed magnet name.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(PUDetailWindow, parent=None, devname=args.pmname)
sys.exit(app.exec_())
