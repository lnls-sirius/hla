#!/usr/bin/env python-sirius

"""Lauch PVs configuration manager."""
import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_configdb.pvsconfmgr import PVsConfigManager


if __name__ == '__main__':
    app = SiriusApplication()
    w = PVsConfigManager()
    w.show()
    sys.exit(app.exec_())
