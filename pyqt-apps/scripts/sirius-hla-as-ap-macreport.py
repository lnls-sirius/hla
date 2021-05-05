#!/usr/bin/env python-sirius

"""Interface to handle offline current/strengths conversions."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ap_macreport import MacReportWindow


app = SiriusApplication()
app.open_window(MacReportWindow)
sys.exit(app.exec_())
