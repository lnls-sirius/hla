#!/usr/bin/env python-sirius

"""Window to equalize switching semicycles of BPM antennas."""

import sys
import argparse as _argparse

from siriuspy.logging import configure_logging
from siriushla.sirius_application import SiriusApplication
from siriushla.si_di_equalize_bpms import BPMsEqualizeSwitching


parser = _argparse.ArgumentParser(
    description="Run BPMs Equalization Interface.")
args = parser.parse_args()

configure_logging()

app = SiriusApplication()
app.open_window(BPMsEqualizeSwitching, parent=None)
sys.exit(app.exec_())
