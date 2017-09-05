#!/usr/bin/env python-sirius

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import SiriusMagnetControlWindow
from siriushla import util

app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = SiriusMagnetControlWindow()
window.show()
sys.exit(app.exec_())
