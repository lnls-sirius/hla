#!/usr/bin/env python-sirius

"""TB PS Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow


parser = _argparse.ArgumentParser(description="Run TB PS Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

app = SiriusApplication()
device = args.device
if device:
    window = PSControlWindow
    kwargs = dict(section='TB', device=device)
else:
    window = PSTabControlWindow
    kwargs = dict(section='TB')
app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
