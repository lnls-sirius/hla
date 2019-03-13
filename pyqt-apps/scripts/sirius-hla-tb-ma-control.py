#!/usr/bin/env python-sirius

"""TB Magnets Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

parser = _argparse.ArgumentParser(description="Run TB MA Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

device = args.device

app = SiriusApplication()
if device:
    window = PSControlWindow(section='TB', discipline='MA', device=device)
else:
    window = PSTabControlWindow(section='TB', discipline='MA')
window.show()
sys.exit(app.exec_())
