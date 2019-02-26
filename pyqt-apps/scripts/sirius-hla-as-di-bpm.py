#!/usr/bin/env python-sirius

"""Open Window of Specified BPM."""

import sys
import argparse as _argparse
from qtpy.QtWidgets import QInputDialog
from siriuspy.envars import vaca_prefix
from siriuspy.search.bpms_search import BPMSearch
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms import SelectBPMs


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified BPM.")
parser.add_argument('sec', type=str, help='Select a section.')
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()


app = SiriusApplication()
BPMsList = create_window_from_widget(SelectBPMs, 'BPMsList', is_main=True)

if args.sec == 'SI':
    sector, ok = QInputDialog.getItem(
        None, 'Chose SI sector', 'Chose a sector number: ',
        ['{:02}'.format(i) for i in range(1, 21)])
    if ok:
        bpms_names = BPMSearch.get_names(
            filters={'sec': args.sec, 'sub': sector+'.*'})
    else:
        bpms_names = BPMSearch.get_names(
            filters={'sec': args.sec, 'sub': '01.*'})
else:
    bpms_names = BPMSearch.get_names(filters={'sec': args.sec})
window = BPMsList(None, prefix=args.prefix, bpm_list=bpms_names)
window.setWindowTitle(args.sec + ' BPM List')
window.show()
sys.exit(app.exec_())
