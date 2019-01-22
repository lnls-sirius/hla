#!/usr/bin/env python-sirius

"""Open Window of Specified Screen."""

import os
import sys
import argparse as _argparse
from siriuspy.envars import vaca_prefix
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QSpacerItem, \
                           QSizePolicy as QSzPlcy, QGridLayout
from pydm.widgets import PyDMEnumComboBox, PyDMLabel
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusScrnView, PyDMLed
from siriushla.widgets.windows import SiriusMainWindow


parser = _argparse.ArgumentParser(
    description="Run Interface of Specified Screen.")
parser.add_argument('scrn', type=str, default='TB-01:DI-Scrn-1',
                    help='Select Screen.')
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()

scrn_device = args.scrn
prefix = args.prefix

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '200000000'
app = SiriusApplication()

cw = QWidget()
scrn_view = SiriusScrnView(prefix=prefix, device=scrn_device)
cb_scrntype = PyDMEnumComboBox(
    parent=cw, init_channel=prefix+scrn_device+':ScrnType-Sel')
l_scrntype = PyDMLabel(
    parent=cw, init_channel=prefix+scrn_device+':ScrnType-Sts')
led_movests = PyDMLed(
    parent=cw, init_channel=prefix+scrn_device+':DoneMov-Mon',
    color_list=[PyDMLed.LightGreen, PyDMLed.DarkGreen])
led_movests.shape = 2
led_movests.setStyleSheet("""min-height:1.29em; max-height:1.29em;""")

lay = QGridLayout()
lay.addWidget(QLabel('<h3>Screen View</h3>',
                     cw, alignment=Qt.AlignCenter), 0, 0, 1, 3)
lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 1, 0)
lay.addWidget(QLabel('Select Screen Type: ', cw,
                     alignment=Qt.AlignRight), 2, 0)
lay.addWidget(cb_scrntype, 2, 1)
lay.addWidget(l_scrntype, 2, 2)
lay.addWidget(QLabel('Motor movement status: ', cw,
                     alignment=Qt.AlignRight), 3, 0)
lay.addWidget(led_movests, 3, 1)

lay.addItem(QSpacerItem(20, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 0)
lay.addWidget(scrn_view, 5, 0, 1, 3)
cw.setLayout(lay)

window = SiriusMainWindow()
window.setWindowTitle('Screen View: '+scrn_device)
window.setCentralWidget(cw)
window.show()
window.setFocus(True)
sys.exit(app.exec_())
