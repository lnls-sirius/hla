#!/usr/bin/env python-sirius

"""Power Supply Cycling Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_cycle.cycle_window import CycleWindow
from siriushla import util


app = SiriusApplication(None, sys.argv)
util.set_style(app)
window = CycleWindow()
window.show()
sys.exit(app.exec_())
