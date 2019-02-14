#!/usr/bin/env python-sirius

"""Power Supply Cycling Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_cycle.cycle_window import CycleWindow


app = SiriusApplication(None, sys.argv)
window = CycleWindow()
window.show()
sys.exit(app.exec_())
