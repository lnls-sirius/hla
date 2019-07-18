#!/usr/bin/env python-sirius

"""SI Configuration Manager Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb.normconfigs import ConfigManagerWindow


app = SiriusApplication(None, sys.argv)
app.open_window(
    ConfigManagerWindow, parent=None, config_type='si_strength_pvs')
sys.exit(app.exec_())
