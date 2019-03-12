#!/usr/bin/env python-sirius

"""TS Magnets Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

parser = _argparse.ArgumentParser(description="Run TS MA Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

device = args.device

app = SiriusApplication()
if device:
    window = PSControlWindow(section='TS', discipline='MA', device=device)
else:
    window = PSTabControlWindow(section='TS', discipline='MA')
window.show()
sys.exit(app.exec_())
