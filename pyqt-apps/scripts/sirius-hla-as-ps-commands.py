#!/usr/bin/env python-sirius

"""Open power supplies commands window."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_commands.main import PSCmdWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Commands Interface.")
args = parser.parse_args()


app = SiriusApplication()
app.open_window(PSCmdWindow)
sys.exit(app.exec_())
