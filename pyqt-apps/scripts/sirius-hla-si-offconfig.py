#!/usr/bin/env python-sirius

"""SI Configuration Manager Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb import ConfigManagerWindow


app = SiriusApplication(None, sys.argv)
window = ConfigManagerWindow('si_strength_pvs')
window.show()
sys.exit(app.exec_())
