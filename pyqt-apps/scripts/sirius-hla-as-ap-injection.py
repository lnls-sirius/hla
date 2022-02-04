#!/usr/bin/env python-sirius

"""Injection Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injection import InjCtrlWindow


app = SiriusApplication(None, sys.argv)
app.open_window(InjCtrlWindow, parent=None)
sys.exit(app.exec_())
