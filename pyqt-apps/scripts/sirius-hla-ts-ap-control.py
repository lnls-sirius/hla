#!/usr/bin/env python-sirius

"""TS High Level Control Window Application."""

import os
import sys
import argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.tl_ap_control.HLTLControl import TLAPControlWindow
from siriushla import util
from siriuspy.envars import vaca_prefix as _vaca_prefix


parser = argparse.ArgumentParser(
                    description="Run TS Control HLA Interface.")
parser.add_argument('-p', "--prefix", type=str, default=_vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()
util.set_style(app)
window = TLAPControlWindow(prefix=args.prefix, tl='ts')
window.show()
sys.exit(app.exec_())
