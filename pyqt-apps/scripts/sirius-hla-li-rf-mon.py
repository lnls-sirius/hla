#!/usr/bin/env python-sirius

"""Linac MPS Monitor."""
import sys
import argparse as _argparse
import qtawesome as _qta
from siriushla import util as _util
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.widgets.windows import create_window_from_widget
from siriushla.li_rf_llrf import LLRFMonitor

parser = _argparse.ArgumentParser(
    description="Run Linac LLRF Control Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
window = create_window_from_widget(
    LLRFMonitor, is_main=True,
    withscroll=True, min_width=100, min_height=55,
    icon=_qta.icon(
        'mdi.waves', color=_util.get_appropriate_color('LI')))
app.open_window(
    window, parent=None, prefix=args.prefix)
sys.exit(app.exec_())
