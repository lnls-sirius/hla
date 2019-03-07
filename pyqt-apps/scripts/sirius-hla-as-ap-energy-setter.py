#!/usr/bin/env python-sirius
"""Energy Setter Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.energy_button import EnergySetterWindow

app = SiriusApplication(None, sys.argv)
window = EnergySetterWindow()
window.show()
sys.exit(app.exec_())
