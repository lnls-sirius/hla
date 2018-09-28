#!/usr/bin/env python-sirius

"""SI Configuration Manager Application."""

import sys
from pydm import PyDMApplication
from siriushla.as_config_manager import ConfigManagerWindow
from siriushla import util


app = PyDMApplication(None, sys.argv)
util.set_style(app)
window = ConfigManagerWindow('si_strength_pvs')
window.show()
sys.exit(app.exec_())
