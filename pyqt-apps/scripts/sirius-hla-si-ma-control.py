#!/usr/bin/env python-sirius

"""SI Magnets Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_ps_control import PSTabControlWindow, PSControlWindow

    parser = _argparse.ArgumentParser(description="Run SI MA Interface.")
    parser.add_argument('-dev', "--device", type=str, default='')
    args = parser.parse_args()

    device = args.device

    app = SiriusApplication()
    if device:
        wclass = PSControlWindow
        kwargs = dict(section='SI', discipline='MA', device=device)
    else:
        wclass = PSTabControlWindow
        kwargs = dict(section='SI', discipline='MA')
    app.open_window(wclass, parent=None, **kwargs)
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
