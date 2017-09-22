#!/usr/bin/env python-sirius

"""TB Magnets Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import TBMagnetControlWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = TBMagnetControlWindow()
window.show()
sys.exit(app.exec_())
