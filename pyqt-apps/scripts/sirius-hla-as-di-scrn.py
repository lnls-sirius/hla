#!/usr/bin/env python-sirius

"""Open Window of Specified Screen."""

import os
import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as PVName
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_scrns import SelectScrns, IndividualScrn


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('scrn_sel', type=str, help='Select a section.')
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()

scrn_sel = PVName(args.scrn_sel)
prefix = args.prefix

if scrn_sel.dev == 'Scrn':
    window = create_window_from_widget(
        IndividualScrn, title='Screen View: '+scrn_sel, is_main=True)
    kwargs = dict(prefix=prefix, scrn=scrn_sel)
else:
    window = create_window_from_widget(
        SelectScrns, title='Select a Screen', is_main=True)
    kwargs = dict(prefix=prefix, sec=scrn_sel)

app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
