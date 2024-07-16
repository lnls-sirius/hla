#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
import qtawesome as qta

from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import BPMSearch
from siriushla.util import get_appropriate_color, get_monitor_icon
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms import SelectBPMs, BPMMain, AcqDataSummary


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument(
    'bpm_sel', type=str, help='Select a section or a BPM name.')
parser.add_argument(
    '-s', '--subsection', type=str, default='all',
    help='Show the ith subgroup of the bpms.' +
         ' The maximum number of groups for BO is 5 and for SI is 20')
parser.add_argument(
    '-w', '--window', type=str, default='Monitor',
    help="type of window to open (default= 'Monitor').",
    choices=('AcqData', 'Monitor'))
parser.add_argument(
    '-m', '--mode', type=str, default='Positions',
    help="Show Antennas or Positions  (default= 'Positions').",
    choices=('Positions', 'Antennas'))
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

app = SiriusApplication()
pv = _PVName(args.bpm_sel)
kwargs = dict()
if pv.dev in ('BPM', 'PBPM'):
    icon = qta.icon('mdi.currency-sign', color=get_appropriate_color(pv.sec))
    window = create_window_from_widget(
        BPMMain, title=args.bpm_sel, is_main=True, icon=icon)
    kwargs.update(dict(prefix=args.prefix, bpm=pv))
else:
    sec = args.bpm_sel.upper()
    bpms_names = BPMSearch.get_names(filters={'sec': sec, 'dev': 'BPM'})
    icon = qta.icon('mdi.currency-sign', color=get_appropriate_color(sec))
    if args.window == 'Monitor':
        clas = SelectBPMs
        icon = get_monitor_icon(
            'mdi.currency-sign', color=get_appropriate_color(sec))
    else:
        clas = AcqDataSummary
        kwargs['mode'] = args.mode
    slc = slice(None, None)
    maxn = 5 if sec == 'BO' else 20
    if args.subsection != 'all':
        sub = int(args.subsection)
        sub = min(sub, maxn)
        siz = len(bpms_names)//maxn
        slc = slice(siz*(sub-1), siz*sub)
    bpms_names = bpms_names[slc]
    window = create_window_from_widget(
        clas, title=sec + ' BPM List', is_main=True, icon=icon)
    kwargs.update(dict(prefix=args.prefix, bpm_list=bpms_names))

app.open_window(window, parent=None, **kwargs)
sys.exit(app.exec_())
