#!/usr/bin/env python-sirius

"""Lauch configuration database manager."""
import sys

from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb import ConfigurationManager

app = SiriusApplication()
model = ConfigDBClient()
widget = ConfigurationManager(model)
widget.show()
sys.exit(app.exec_())
