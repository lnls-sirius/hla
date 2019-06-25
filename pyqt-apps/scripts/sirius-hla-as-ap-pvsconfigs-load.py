#!/usr/bin/env python-sirius

"""Lauch PVs configuration manager."""
import sys
from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb.pvsconfigs import \
    LoadAndApplyConfig2MachineWindow


app = SiriusApplication()
client = ConfigDBClient()
app.open_window(LoadAndApplyConfig2MachineWindow, parent=None, client=client)
sys.exit(app.exec_())
