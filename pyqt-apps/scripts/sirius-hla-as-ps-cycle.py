#!/usr/bin/env python-sirius

"""Power Supply Cycling Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ps_cycle import PsCycleWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = PsCycleWindow()
window.show()
sys.exit(app.exec_())
