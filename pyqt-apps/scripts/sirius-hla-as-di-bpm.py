#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import BPMSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms import SelectBPMs, BPMMain, SinglePassSummary, \
    MultiTurnSummary


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument(
    'bpm_sel', type=str, help='Select a section or a BPM name.')
parser.add_argument(
    '-s', '--subsection', type=str, default='all',
    help='Subdivide take the nth subgroup of the bpms.',
    choices=('all', '1', '2', '3', '4', '5'))
parser.add_argument(
    '-w', '--window', type=str, default='Summary',
    help="type of window to open (default= 'Summary').",
    choices=('SPass', 'MTurn', 'Summary'))
parser.add_argument(
    '-p', "--prefix", type=str, default=vaca_prefix,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
pv = _PVName(args.bpm_sel)
if pv.dev == 'BPM':
    window = create_window_from_widget(
        BPMMain, title=args.bpm_sel, is_main=True)
    kwargs = dict(prefix=args.prefix, bpm=pv)
else:
    bpms_names = BPMSearch.get_names(filters={'sec': args.bpm_sel.upper()})
    if args.window == 'Summary':
        clas = SelectBPMs
    elif args.window == 'SPass':
        clas = SinglePassSummary
    else:
        clas = MultiTurnSummary
    slc = slice(None, None)
    if args.subsection != 'all':
        sub = int(args.subsection)
        siz = len(bpms_names)//5
        slc = slice(siz*(sub-1), siz*sub)
    bpms_names = bpms_names[slc]
    window = create_window_from_widget(
        clas, title=args.bpm_sel.upper() + ' BPM List', is_main=True)
    kwargs = dict(prefix=args.prefix, bpm_list=bpms_names)

app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
