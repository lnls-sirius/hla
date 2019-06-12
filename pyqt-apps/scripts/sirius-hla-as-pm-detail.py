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
window = PulsedMagnetDetailWindow(maname=args.pmname)
window.show()
sys.exit(app.exec_())
