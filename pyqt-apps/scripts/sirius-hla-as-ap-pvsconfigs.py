#!/usr/bin/env python-sirius

"""Lauch PVs configuration manager."""
import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb.pvsconfigs import PVsConfigManager


app = SiriusApplication()
app.open_window(PVsConfigManager)
sys.exit(app.exec_())
