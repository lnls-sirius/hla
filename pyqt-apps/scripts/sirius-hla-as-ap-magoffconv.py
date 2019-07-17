#!/usr/bin/env python-sirius

"""Interface to handle offline current/strengths conversions."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_ap_magoffconv import MagOffConvApp

    parser = _argparse.ArgumentParser(description="Run Offline Converter App.")
    args = parser.parse_args()

    app = SiriusApplication()
    app.open_window(MagOffConvApp)
    sys.exit(app.exec_())
except:
    app = SiriusApplication()
    app.disclaimer()
