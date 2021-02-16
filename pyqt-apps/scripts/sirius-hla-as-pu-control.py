#!/usr/bin/env python-sirius

"""AS PM Application."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.as_pu_control import PUControlWindow


parser = _argparse.ArgumentParser(description="Run PU Interface.")
parser.add_argument(
    '-g', "--groups", type=str, default='function',
    choices=('function', 'sectors'))
args = parser.parse_args()

main_secs = ('InjBO', 'EjeBO', 'InjSI') if args.groups == 'function' \
    else ('TB', 'BO', 'TS', 'SI')

app = SiriusApplication()
app.open_window(
    PUControlWindow, parent=None, section='AS', is_main=True,
    main_secs=main_secs)
sys.exit(app.exec_())
