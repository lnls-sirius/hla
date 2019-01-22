#!/usr/local/env python-sirius

"""BO Configuration Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ap_servconf import ConfigManagerWindow


app = PyDMApplication(None, sys.argv)
window = ConfigManagerWindow('bo_normalized')
window.show()
sys.exit(app.exec_())
