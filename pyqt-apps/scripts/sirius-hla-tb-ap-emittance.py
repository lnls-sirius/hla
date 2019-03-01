#!/usr/bin/env python-sirius

"""Open Window of emittance measurement in TB."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_measure import EmittanceMeasure


parser = _argparse.ArgumentParser(
    description="Run Interface of emittance measurement in TB.")
parser.add_argument('-p', "--place", type=str, default='TB-QF2A',
                    help="Define which quadrupole to use.")
args = parser.parse_args()

app = SiriusApplication()
window = EmittanceMeasure(place=args.place)
window.show()
sys.exit(app.exec_())
