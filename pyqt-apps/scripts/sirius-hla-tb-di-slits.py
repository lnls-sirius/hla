#!/usr/bin/env python-sirius

"""Open Window to control TB Slits widgets."""

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
    description="Run Interface to control TB Slits widgets.")
parser.add_argument('-p', "--prefix", type=str, default=vaca_prefix,
                    help="Define the prefix for the PVs in the window.")
args = parser.parse_args()
prefix = args.prefix

app = SiriusApplication()
util.set_style(app)


class _cw(QWidget):

    def __init__(self, parent=None):
        super(_cw, self).__init__(None)
        gbox_slith = QGroupBox('TB-01:DI-SlitH')
        self.slith = SlitMonitoring('H', self, prefix)
        lay_slith = QVBoxLayout()
        lay_slith.addWidget(self.slith)
        gbox_slith.setLayout(lay_slith)

        gbox_slitv = QGroupBox('TB-01:DI-SlitV')
        self.slitv = SlitMonitoring('V', self, prefix)
        lay_slitv = QVBoxLayout()
        lay_slitv.addWidget(self.slitv)
        gbox_slitv.setLayout(lay_slitv)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('<h3>TB Slits View</h3>',
                             alignment=Qt.AlignCenter))
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addWidget(gbox_slith)
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addWidget(gbox_slitv)
        lay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed))
        self.setLayout(lay)

    def keyPressEvent(self, event):
        """Override keyPressEvent."""
        super().keyPressEvent(event)
        self.slith.updateSlitWidget()
        self.slitv.updateSlitWidget()


window = SiriusMainWindow()
window.setWindowTitle('Slits View')
window.setCentralWidget(_cw())
window.show()
sys.exit(app.exec_())
