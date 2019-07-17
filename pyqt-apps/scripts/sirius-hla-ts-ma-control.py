#!/usr/bin/env python-sirius

"""TS Magnets Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

    parser = _argparse.ArgumentParser(description="Run TS MA Interface.")
    parser.add_argument('-dev', "--device", type=str, default='')
    args = parser.parse_args()

    device = args.device

    app = SiriusApplication()
    if device:
        window = PSControlWindow
        kwargs = dict(section='TS', discipline='MA', device=device)
    else:
        window = PSTabControlWindow
        kwargs = dict(section='TS', discipline='MA')
    app.open_window(window, parent=None, **kwargs)
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
