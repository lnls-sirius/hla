#!/usr/bin/env python-sirius

"""Open power supplies test window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_test.ps_test_window import PSTestWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Cycling Interface.")
parser.add_argument('-isadv', action='store_true')
args = parser.parse_args()
isadv = args.isadv


app = SiriusApplication()
app.open_window(PSTestWindow, adv_mode=isadv)
sys.exit(app.exec_())
