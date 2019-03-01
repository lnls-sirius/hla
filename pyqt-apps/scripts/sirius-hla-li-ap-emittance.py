#!/usr/bin/env python-sirius

"""Open Window of emittance measurement in Linac."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_measure import EmittanceMeasure


parser = _argparse.ArgumentParser(
    description="Run Interface of emittance measurement in Linac.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = EmittanceMeasure(place='LI')
window.show()
sys.exit(app.exec_())
