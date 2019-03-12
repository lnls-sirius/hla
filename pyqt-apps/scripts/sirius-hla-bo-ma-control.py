#!/usr/local/env python-sirius

"""BO Magnets Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

parser = _argparse.ArgumentParser(description="Run BO PS Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

device = args.device

app = SiriusApplication()
if device:
    window = PSControlWindow(section='BO', discipline='MA', device=device)
else:
    window = PSTabControlWindow(section='BO', discipline='MA')
window.show()
sys.exit(app.exec_())
