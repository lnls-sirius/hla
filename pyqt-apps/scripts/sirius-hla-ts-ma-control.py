#!/usr/bin/env python-sirius

"""TS Magnets Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import TSMagnetControlWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = TSMagnetControlWindow()
window.show()
sys.exit(app.exec_())
