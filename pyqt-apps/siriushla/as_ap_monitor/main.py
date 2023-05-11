"""Sirius Monitor."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout

from siriuspy.envars import VACA_PREFIX

from ..as_ti_control import MonitorWindow as TIMonitor
from ..li_ap_mps import MPSMonitor as LIMPSMonitor
from ..as_ps_diag import PSMonitor
from .util import get_label2devices, get_sec2dev_laypos


class SiriusMonitor(QWidget):
    """Sirius Monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX, args=None):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._args = args
        self.setObjectName('ASApp')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>Sirius Monitor</h3>',
                       alignment=Qt.AlignCenter)
        label.setStyleSheet('max-height:1.29em;')

        self.wid_asmon = PSMonitor(
            self, self._prefix,
            get_label2devices_method=get_label2devices,
            get_sec2devlaypos_method=get_sec2dev_laypos)
        self.wid_asmon.title.setText('<h3>PS, PU & RF</h3>')
        self.wid_asmon.setStyleSheet("""
            QLed{
                min-height: 0.98em; max-height: 0.98em;
                min-width: 0.98em; max-width: 0.98em;}""")

        self.wid_timon = TIMonitor(self, self._prefix)
        self.wid_timon.title.setText('<h3>TI</h3>')
        self.wid_timon.setStyleSheet("""
            QLed{
                min-height: 0.98em; max-height: 0.98em;
                min-width: 0.98em; max-width: 0.98em;}""")

        self.wid_mpsmon = LIMPSMonitor(self, self._prefix)
        self.wid_mpsmon.title.setText('<h3>LI MPS</h3>')
        self.wid_mpsmon.setObjectName('ASApp')
        self.wid_mpsmon.setStyleSheet("""
            QLabel { qproperty-alignment: AlignCenter; }
            QLed{
                min-height: 0.98em; max-height: 0.98em;
                min-width: 0.98em; max-width: 0.98em;}""")

        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.addWidget(label, 0, 0, 1, 3)
        layout.addWidget(self.wid_asmon, 1, 0, alignment=Qt.AlignTop)
        layout.addWidget(self.wid_timon, 1, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.wid_mpsmon, 1, 2, alignment=Qt.AlignTop)
