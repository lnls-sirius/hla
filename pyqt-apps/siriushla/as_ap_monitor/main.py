"""Sirius Monitor."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX

from siriushla.widgets import SiriusMainWindow
from siriushla.as_ti_control import MonitorWindow as TIMonitor
from siriushla.li_ap_mps import MPSMonitor as LIMPSMonitor
from siriushla.util import get_appropriate_color
from siriushla.as_ps_diag import PSMonitor
from .util import get_label2devices, get_sec2dev_laypos


class SiriusMonitor(SiriusMainWindow):
    """Sirius Monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setObjectName('ASApp')
        self.setWindowTitle('Sirius Monitor')
        color = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.monitor-dashboard', color=color))
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h2>Sirius Monitor</h2>',
                       alignment=Qt.AlignCenter)
        label.setStyleSheet('max-height:1.29em;')

        cw = QWidget()
        self.setCentralWidget(cw)

        self.wid_asmon = PSMonitor(
            self, self._prefix,
            get_label2devices_method=get_label2devices,
            get_sec2devlaypos_method=get_sec2dev_laypos)
        self.wid_asmon.title.setText('<h2>PS, PU & RF</h2>')

        self.wid_timon = TIMonitor(self, self._prefix)

        self.wid_mpsmon = LIMPSMonitor(self, self._prefix)
        self.wid_mpsmon.setObjectName('ASApp')

        layout = QGridLayout(cw)
        layout.setHorizontalSpacing(12)
        layout.addWidget(label, 0, 0, 1, 3)
        layout.addWidget(self.wid_asmon, 1, 0, alignment=Qt.AlignTop)
        layout.addWidget(self.wid_timon, 1, 1, alignment=Qt.AlignTop)
        layout.addWidget(self.wid_mpsmon, 1, 2, alignment=Qt.AlignTop)
