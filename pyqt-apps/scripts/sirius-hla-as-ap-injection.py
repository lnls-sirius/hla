#!/usr/bin/env python-sirius

"""Injection Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_injection import InjectionController, InjectionWindow


app = SiriusApplication(None, sys.argv)
controller = InjectionController()
window = InjectionWindow(controller)
window.show()
sys.exit(app.exec_())
