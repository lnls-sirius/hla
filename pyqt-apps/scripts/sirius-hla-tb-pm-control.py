#!/usr/bin/env python-sirius

"""TB PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow


app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, is_main=False, section='TB')
sys.exit(app.exec_())
