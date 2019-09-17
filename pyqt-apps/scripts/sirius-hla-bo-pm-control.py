#!/usr/bin/env python-sirius

"""BO PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow


app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, is_main=False, section='BO')
sys.exit(app.exec_())
