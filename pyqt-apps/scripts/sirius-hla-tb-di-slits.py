#!/usr/bin/env python-sirius

"""Open Window of Specified Screen."""

import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGroupBox, QSpacerItem, \
                           QSizePolicy as QSzPlcy, QVBoxLayout
from siriushla.sirius_application import SiriusApplication
from siriushla.tl_ap_control import SlitMonitoring
from siriushla import util
from siriushla.widgets.windows import SiriusMainWindow


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()
prefix = args.prefix

app = SiriusApplication()
util.set_style(app)

cw = QWidget()
gbox_slith = QGroupBox('TB-01:DI-SlitH')
lay_slith = QVBoxLayout()
lay_slith.addWidget(SlitMonitoring('H', cw, prefix))
gbox_slith.setLayout(lay_slith)
gbox_slitv = QGroupBox('TB-01:DI-SlitV')
lay_slitv = QVBoxLayout()
lay_slitv.addWidget(SlitMonitoring('V', cw, prefix))
gbox_slitv.setLayout(lay_slitv)

lay = QVBoxLayout()
lay.addWidget(QLabel('<h3>TB Slits View</h3>', alignment=Qt.AlignCenter))
lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
lay.addWidget(gbox_slith)
lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
lay.addWidget(gbox_slitv)
lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
cw.setLayout(lay)

window = SiriusMainWindow()
window.setWindowTitle('Slits View')
window.setCentralWidget(cw)
window.show()
sys.exit(app.exec_())
