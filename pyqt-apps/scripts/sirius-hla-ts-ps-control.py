#!/usr/bin/env python-sirius

"""TS PS Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

parser = _argparse.ArgumentParser(description="Run TS PS Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

device = args.device

app = SiriusApplication()
if device:
    window = PSControlWindow(section='TS', discipline='PS', device=device)
else:
    window = PSTabControlWindow(section='TS', discipline='PS')
window.show()
sys.exit(app.exec_())
