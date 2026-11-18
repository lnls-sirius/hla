"""S3PW Compressors Module."""

from qtpy.QtWidgets import QFrame, QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.util import connect_newprocess, connect_window
from siriushla.widgets import PyDMStateButton
from siriushla.widgets.dialog import StatusDetailDialog

from ..base import IDCommonControlWindow, IDCommonDialog, IDCommonSummaryBase


class S3PWCompressors(IDCommonDialog):
    def __init__(self, parent=None, prefix='', device='', title=''):
        super().__init__(parent, prefix, device, title)

    def _setupUi(self):
        gbox = QGroupBox('Heaters Status', self)
        glay = QGridLayout(gbox)

    def _compressorGroupDetail(self):
        group = QGroupBox("Compressor")
        lay = QGridLayout(group)
        lay.setContentsMargins(12,12,12,12)

        lbl = QLabel("Start Group", alignment=Qt.AlignHCenter)
        btn = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="AllCompEnbl-Sel")
        )
        lay.addWidget(lbl, 0, 0)
        lay.addWidget(btn, 0, 1)

        lb_glob = QLabel("Compressor 1", alignment=Qt.AlignHCenter)
        self.bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="Comp1Enbl-Sel")
        )
        lay.addWidget(lb_glob, 1, 0)
        lay.addWidget(self.bt_idffglob, 1, 1)

        lb_glob = QLabel("Compressor 2", alignment=Qt.AlignHCenter)
        self.bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="Comp2Enbl-Sel")
        )
        lay.addWidget(lb_glob, 2, 0)
        lay.addWidget(self.bt_idffglob, 2, 1)

        lb_glob = QLabel("Compressor 3", alignment=Qt.AlignHCenter)
        self.bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="Comp3Enbl-Sel")
        )
        lay.addWidget(lb_glob, 3, 0)
        lay.addWidget(self.bt_idffglob, 3, 1)

        lb_glob = QLabel("Compressor 4", alignment=Qt.AlignHCenter)
        self.bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="Comp4Enbl-Sel")
        )
        lay.addWidget(lb_glob, 4, 0)
        lay.addWidget(self.bt_idffglob, 4, 1)

        return group