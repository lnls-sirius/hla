#!/usr/bin/env python-sirius

import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import SiriusMagnetControlWindow


app = PyDMApplication(None, sys.argv)
window = SiriusMagnetControlWindow()
window.show()
sys.exit(app.exec_())
