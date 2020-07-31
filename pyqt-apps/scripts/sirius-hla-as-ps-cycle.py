#!/usr/bin/env python-sirius

"""Power Supply Cycling Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_cycle.cycle_window import CycleWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Cycling Interface.")
parser.add_argument('-isadv', action='store_true')
args = parser.parse_args()
isadv = args.isadv

app = SiriusApplication(None, sys.argv)
app.open_window(CycleWindow, adv_mode=isadv)
sys.exit(app.exec_())
