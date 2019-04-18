#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import BPMSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.as_interlocks import Interlocks

parser = _argparse.ArgumentParser(
    description="Run Interlocks Window.")
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = Interlocks(prefix=args.prefix)
window.show()
sys.exit(app.exec_())
