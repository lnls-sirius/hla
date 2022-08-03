#!/usr/bin/env python-sirius

"""SI PS Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow, \
    PSTrimWindow


parser = _argparse.ArgumentParser(description="Run SI PS Interface.")
parser.add_argument('-dev', '--device', type=str, default='')
parser.add_argument('-sub', '--subsection', type=str, default='')
parser.add_argument('-istrim', action='store_true')
args = parser.parse_args()

app = SiriusApplication()
dev = args.device
sub = args.subsection
istrim = args.istrim
if dev and dev != 'all':
    if not istrim:
        window = PSControlWindow
        kwargs = dict(section='SI', device=dev)
        if sub:
            kwargs.update({'subsection': sub})
    else:
        window = PSTrimWindow
        kwargs = dict(device=dev)
else:
    window = PSTabControlWindow
    kwargs = dict(section='SI')
app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
