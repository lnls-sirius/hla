#!/usr/bin/env python-sirius

"""SI Injection Trajectory Fitting Application."""

import sys
import argparse as _argparse

from siriushla.sirius_application import SiriusApplication
from siriushla.si_di_equalize_bpms import BPMsEqualizeSwitching


parser = _argparse.ArgumentParser(
    description="Run BPMs Equalization Interface.")
args = parser.parse_args()

app = SiriusApplication()
app.open_window(BPMsEqualizeSwitching, parent=None)
sys.exit(app.exec_())
