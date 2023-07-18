#!/usr/bin/env python-sirius

"""EVE GUI."""

import sys
import argparse as _argparse

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import EVE
from siriushla.util import get_appropriate_color

parser = _argparse.ArgumentParser(description="Run EVE GUI.")
parser.add_argument(
    'device', type=str, help='Select a device')
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication(None, sys.argv)
icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
window = create_window_from_widget(
    EVE, title=args.device, icon=icon, is_main=True)
app.open_window(window, parent=None, device=args.device, prefix=args.prefix)
sys.exit(app.exec_())
