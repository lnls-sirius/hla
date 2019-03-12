"""Interface to handle main operation commands."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_operation import MainOperation


parser = _argparse.ArgumentParser(
    description="Run Operation Interface.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()


app = SiriusApplication()
window = MainOperation(prefix=args.prefix)
window.show()
sys.exit(app.exec_())
