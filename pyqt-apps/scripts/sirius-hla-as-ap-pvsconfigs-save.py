#!/usr/bin/env python-sirius

"""Lauch PVs configuration manager."""
import sys
from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.clientconfigdb import ConfigDBClient
    from siriushla.as_ap_configdb.pvsconfigs import \
        ReadAndSaveConfig2ServerWindow

    app = SiriusApplication()
    client = ConfigDBClient()
    app.open_window(ReadAndSaveConfig2ServerWindow, parent=None, client=client)
    sys.exit(app.exec_())
except:
    app = SiriusApplication()
    app.disclaimer()
