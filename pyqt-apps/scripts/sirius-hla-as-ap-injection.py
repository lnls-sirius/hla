#!/usr/bin/env python-sirius

"""Injection Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injection import InjectionController, InjectionWindow


app = SiriusApplication(None, sys.argv)
ctlr = InjectionController()
app.open_window(InjectionWindow, parent=None, controller=ctlr)
sys.exit(app.exec_())
