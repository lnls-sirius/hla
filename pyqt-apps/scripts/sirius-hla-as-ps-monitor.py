"""Interface to handle general status."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_diag import PSMonitor


parser = _argparse.ArgumentParser(
    description="Run Power Supply Monitor Interface.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()


app = SiriusApplication()
# when operating with all sections, remove 'sections' argument
window = PSMonitor(prefix=args.prefix, sections=['LI', 'TB', 'BO'])
window.show()
sys.exit(app.exec_())
