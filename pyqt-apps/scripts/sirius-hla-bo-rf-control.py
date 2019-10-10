#!/usr/bin/env python-sirius

"""PS detailed window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_rf_control import RFStatus


parser = _argparse.ArgumentParser(
    description="Run RF Control Interface.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(RFStatus)
sys.exit(app.exec_())
