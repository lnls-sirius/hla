#!/usr/bin/env python-sirius

"""TS PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PulsedMagnetControlWindow


app = SiriusApplication()
app.open_window(
    PulsedMagnetControlWindow, parent=None, is_main=False, section='TS')
sys.exit(app.exec_())
