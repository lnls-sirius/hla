#!/usr/local/env python-sirius

"""BO Configuration Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ap_servconf import ConfigManagerWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = ConfigManagerWindow('bo_normalized')
window.show()
sys.exit(app.exec_())
