#!/usr/bin/env python-sirius

"""BO PM Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow

parser = _argparse.ArgumentParser(description="Run PU Interface.")
parser.add_argument(
    '-s', "--section", type=str, default='BO',
    choices=('BO', 'InjBO', 'EjeBO'))
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, section=args.section, devtype='PU',
    is_main=False)
sys.exit(app.exec_())
