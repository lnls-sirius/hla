#!/usr/bin/env python-sirius

"""SI PM Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_cryo import CryoMain

parser = _argparse.ArgumentParser(description="Run Cryogenic Interface.")

app = SiriusApplication()
app.open_window(
    CryoMain, parent=None)
sys.exit(app.exec_())
