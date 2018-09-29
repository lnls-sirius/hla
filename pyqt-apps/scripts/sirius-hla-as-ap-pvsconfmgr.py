#!/usr/bin/env python-sirius

"""Lauch PVs configuration manager."""
import sys

from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_pvsconfmgr.configuration_window import ConfigurationWindow
from siriuspy.servconf.conf_service import ConfigService

app = SiriusApplication()
db = ConfigService()
w = ConfigurationWindow(db)
w.show()

sys.exit(app.exec_())
