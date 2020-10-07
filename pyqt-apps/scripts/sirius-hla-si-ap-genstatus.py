#!/usr/bin/env python-sirius
"""Sirius General Status Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_genstatus import SIGenStatusWindow


app = SiriusApplication(None, sys.argv)
app.open_window(SIGenStatusWindow, parent=None)
sys.exit(app.exec_())
