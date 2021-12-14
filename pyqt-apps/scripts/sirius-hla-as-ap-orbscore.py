#!/usr/bin/env python-sirius

"""Interface to orbit score calculations."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_orbscore import OrbitScoreWindow


app = SiriusApplication()
app.open_window(OrbitScoreWindow)
sys.exit(app.exec_())
