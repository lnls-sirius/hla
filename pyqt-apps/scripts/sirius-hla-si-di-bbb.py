"""Open SI BbB Window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.si_di_bbb import BbBMainWindow


parser = _argparse.ArgumentParser(
    description="Run Interface to control SI BbB.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
prefix = args.prefix
app.open_window(BbBMainWindow, parent=None, prefix=prefix)
sys.exit(app.exec_())
