#!/usr/bin/env python-sirius

"""Interface to handle general status."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriuspy.envars import VACA_PREFIX
from siriushla.as_ps_diag.ps_graph_mon import PSGraphMonWindow


parser = _argparse.ArgumentParser(
    description="Run Power Supply Monitor Interface.")
parser.add_argument(
    '-p', "--prefix", type=str, default=VACA_PREFIX,
    help="Define the prefix for the PVs in the window.")
parser.add_argument('-sec', '--section', type=str, default='')
parser.add_argument('-dev', '--device', type=str, default='')
args = parser.parse_args()

if args.section:
    filters = {'sec': args.section, 'sub': '(?!Fam).*', 'dev': args.device}
else:
    filters = ''
app = SiriusApplication()
app.open_window(
    PSGraphMonWindow, parent=None, prefix=args.prefix, filters=filters)
sys.exit(app.exec_())
