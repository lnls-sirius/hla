#!/usr/bin/env python-sirius

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control import PlotWfmErrorWindow

app = SiriusApplication()
app.open_window(PlotWfmErrorWindow)
sys.exit(app.exec_())
