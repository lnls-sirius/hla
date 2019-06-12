#!/usr/local/env python-sirius

"""BO Configuration Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb import ConfigManagerWindow


app = SiriusApplication(None, sys.argv)
window = ConfigManagerWindow('bo_normalized')
window.show()
sys.exit(app.exec_())
