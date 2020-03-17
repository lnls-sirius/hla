#!/usr/bin/env python-sirius

"""Interface to handle offline current/strengths conversions."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_magoffconv import MagOffConvApp


app = SiriusApplication()
app.open_window(MagOffConvApp)
sys.exit(app.exec_())
