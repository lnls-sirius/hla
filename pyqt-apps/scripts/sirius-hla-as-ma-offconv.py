#!/usr/bin/env python-sirius

"""Interface to handle offline current/strengths conversions."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ma_offconv import OffConvApp


parser = _argparse.ArgumentParser(description="Run Offline Converter App.")
args = parser.parse_args()


app = SiriusApplication()
window = OffConvApp()
window.show()
sys.exit(app.exec_())
