#!/usr/local/env python-sirius

"""BO Magnets Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import BoosterMagnetControlWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = BoosterMagnetControlWindow()
window.show()
sys.exit(app.exec_())
