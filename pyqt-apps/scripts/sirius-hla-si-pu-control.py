#!/usr/bin/env python-sirius

"""SI PM Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow

parser = _argparse.ArgumentParser(description="Run PU Interface.")
parser.add_argument(
    '-s', "--section", type=str, default='SI',
    choices=('SI', 'InjSI', 'PingSI'))
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, section=args.section, is_main=False)
sys.exit(app.exec_())
