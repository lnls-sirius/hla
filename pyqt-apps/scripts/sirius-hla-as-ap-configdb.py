#!/usr/bin/env python-sirius

"""Lauch configuration database manager."""
import sys

from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.clientconfigdb import ConfigDBClient
    from siriushla.as_ap_configdb import ConfigurationManager
    app = SiriusApplication()
    model = ConfigDBClient()
    app.open_window(ConfigurationManager, parent=None, model=model)
    sys.exit(app.exec_())
except:
    app = SiriusApplication()
    app.disclaimer()
