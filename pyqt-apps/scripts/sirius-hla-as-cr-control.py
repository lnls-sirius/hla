#!/usr/bin/env python-sirius

"""SI PM Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_cr_control import CryoControl

parser = _argparse.ArgumentParser(description="Run Cryogenic Plant Interface.")
parser.add_argument('-screen', type=str, default='All',
    help='Select the screen of the Cryogenic GUI')
args = parser.parse_args()


app = SiriusApplication()

app.open_window(
    CryoControl, parent=None, screen=args.screen)
sys.exit(app.exec_())
