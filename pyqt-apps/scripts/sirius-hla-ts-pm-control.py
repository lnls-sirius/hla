#!/usr/bin/env python-sirius

"""TS PM Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pm_control import PulsedMagnetControlWindow


app = SiriusApplication()
window = PulsedMagnetControlWindow(is_main=False, section='TS')
window.show()
sys.exit(app.exec_())
