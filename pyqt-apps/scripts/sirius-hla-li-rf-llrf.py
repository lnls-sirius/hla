#!/usr/bin/env python-sirius

"""Linac MPS Monitor."""
import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.li_rf_llrf import MainWindow


parser = _argparse.ArgumentParser(
    description="Run Linac LLRF Control Interface.")
parser.parse_args()

app = SiriusApplication()
app.open_window(MainWindow, parent=None)
sys.exit(app.exec_())
