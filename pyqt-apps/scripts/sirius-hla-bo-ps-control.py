#!/usr/bin/env python-sirius

"""BO PS Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow


parser = _argparse.ArgumentParser(description="Run BO PS Interface.")
parser.add_argument('-dev', "--device", type=str, default='')
args = parser.parse_args()

app = SiriusApplication()
dev = args.device
if dev and dev != 'all':
    window = PSControlWindow
    kwargs = dict(section='BO', device=dev)
else:
    window = PSTabControlWindow
    kwargs = dict(section='BO')
app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
