#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms import BPMMain


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument('bpm', type=str, help='Select BPM.')
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
BPM = create_window_from_widget(BPMMain, 'BPMMainWindow', is_main=True)
window = BPM(None, prefix=args.prefix, bpm=args.bpm)
window.show()
sys.exit(app.exec_())
