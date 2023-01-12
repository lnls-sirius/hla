#!/usr/bin/env python-sirius

"""Open power supplies commands window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_commands.main import PSCmdWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Test Interface.")
parser.add_argument('-isadv', action='store_true')
args = parser.parse_args()
isadv = args.isadv


app = SiriusApplication()
app.open_window(PSCmdWindow, adv_mode=isadv)
sys.exit(app.exec_())
