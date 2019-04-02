#!/usr/bin/env python-sirius

"""PS detailed window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSDetailWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Detailed Control Interface.")
parser.add_argument("psname", type=str, help="PS name.")
args = parser.parse_args()


app = SiriusApplication()
window = PSDetailWindow(parent=None, psname=args.psname)
window.show()
sys.exit(app.exec_())
