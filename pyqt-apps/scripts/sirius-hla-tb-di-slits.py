#!/usr/bin/env python-sirius

"""Open Window to control TB Slits widgets."""

import sys
import argparse as _argparse
from siriushla.sirius_application import SiriusApplication

try:
    from siriuspy.envars import vaca_prefix
    from siriushla.tl_ap_control import SlitsView
    from siriushla.widgets.windows import create_window_from_widget

    parser = _argparse.ArgumentParser(
        description="Run Interface to control TB Slits widgets.")
    parser.add_argument(
        '-p', "--prefix", type=str, default=vaca_prefix,
        help="Define the prefix for the PVs in the window.")
    args = parser.parse_args()
    prefix = args.prefix
    app = SiriusApplication()
    window = create_window_from_widget(
        SlitsView, title='Slits View', is_main=True)
    app.open_window(window, parent=None, prefix=prefix)
    sys.exit(app.exec_())
except:
    app = SiriusApplication()
    app.disclaimer()
