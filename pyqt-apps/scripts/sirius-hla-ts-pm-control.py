#!/usr/bin/env python-sirius

"""TS PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_pm_control import PulsedMagnetControlWindow

    app = SiriusApplication()
    app.open_window(
        PulsedMagnetControlWindow, parent=None, is_main=False, section='TS')
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
