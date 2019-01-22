#!/usr/bin/env python-sirius

"""SI Configuration Manager Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_ap_servconf import ConfigManagerWindow


app = PyDMApplication(None, sys.argv)
window = ConfigManagerWindow('si_strength_pvs')
window.show()
sys.exit(app.exec_())
