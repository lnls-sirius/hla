#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import BPMSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms import SelectBPMs, BPMMain, SinglePassSummary


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument(
    'bpm_sel', type=str, help='Select a section or a BPM name.')
parser.add_argument(
    '-s', '--singlepass', action='store_true', default=False,
    help='If selected show results of singlePass data for all BPMs.')
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
pv = _PVName(args.bpm_sel)
if pv.dev == 'BPM':
    BPMMainWin = create_window_from_widget(
        BPMMain, title=args.bpm_sel, is_main=True)
    window = BPMMainWin(None, prefix=args.prefix, bpm=pv)
else:
    bpms_names = BPMSearch.get_names(filters={'sec': args.bpm_sel.upper()})
    clas = SinglePassSummary if args.singlepass else SelectBPMs
    BPMsList = create_window_from_widget(
        clas, title=args.bpm_sel.upper() + ' BPM List', is_main=True)
    window = BPMsList(None, prefix=args.prefix, bpm_list=bpms_names)

window.show()
sys.exit(app.exec_())
