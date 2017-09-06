#!/usr/bin/env python-sirius

"""TB Magnets Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import ToBoosterMagnetControlWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = ToBoosterMagnetControlWindow()
window.show()
sys.exit(app.exec_())
