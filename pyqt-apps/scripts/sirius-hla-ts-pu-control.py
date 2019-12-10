#!/usr/bin/env python-sirius

"""TS PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow


app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, section='TS', is_main=False)
sys.exit(app.exec_())
