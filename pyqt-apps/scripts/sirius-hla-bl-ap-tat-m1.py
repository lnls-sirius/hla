#!/usr/bin/env python-sirius

"""TATU Mirror Control Window."""

import sys as sys
import argparse as argparse
from siriushla.sirius_application import SiriusApplication
from siriushla.bl_ap_tat_m1 import BLTATMirror


app = SiriusApplication()
app.open_window(
    BLTATMirror, parent=None, mirror='TAT:A:PP01:A')

sys.exit(app.exec_())
