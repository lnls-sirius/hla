#!/usr/bin/env python-sirius

"""TATU Mirror Control Window."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.bl_ap_tat_m1 import BLTATMirror


parser = argparse.ArgumentParser(
    description="Run Mirror Control Window.")
parser.add_argument('mirror', type=str, help='Select a Mirror')
args = parser.parse_args()

app = SiriusApplication()
app.open_window(
    BLTATMirror, parent=None, mirror=args.mirror)

sys.exit(app.exec_())
