#!/usr/bin/env python-sirius

"""SI Magnets Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import SIMagnetControlWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = SIMagnetControlWindow()
window.show()
sys.exit(app.exec_())
