"""BbB Main Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QWidget, QHBoxLayout, \
    QPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..util import connect_window
from ..widgets import SiriusMainWindow
from ..widgets.windows import create_window_from_widget

from .bbb import BbBMainSettingsWidget
from .util import get_bbb_icon, set_bbb_color
from .gpio import BbBGPIOWidget


class BbBMainWindow(SiriusMainWindow):
    """BbB Main Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.setWindowTitle('BbB Control Window')
        self.setObjectName('SIApp')
        self.setWindowIcon(get_bbb_icon())
        self._bbb_widgets = list()
        self._setupUi()

    def _setupUi(self):
        self._ld_bbb = QLabel(
            '<h3>BbB Control Window</h3>', self, alignment=Qt.AlignCenter)

        self._but_fbe = QPushButton('FBE', self)

        window = create_window_from_widget(
            BbBGPIOWidget, title='Front-Back End', icon=get_bbb_icon())
        connect_window(
            self._but_fbe, window, self, prefix=self.prefix,
            device='SI-Glob:DI-BbBProc-L')

        hlay = QHBoxLayout()
        hlay.addWidget(self._but_fbe)
        hlay.addStretch()
        hlay.addWidget(self._ld_bbb)
        hlay.addStretch()

        idcs_types = ['H', 'V', 'L']

        cwt = QWidget(self)
        self.setCentralWidget(cwt)
        lay = QGridLayout(cwt)

        for col, idc in enumerate(idcs_types):
            dev_pref = 'SI-Glob:DI-BbBProc-'+idc

            wid = BbBMainSettingsWidget(self, self.prefix, dev_pref)
            set_bbb_color(wid, dev_pref)
            lay.addWidget(wid, 1, col)
            self._bbb_widgets.append(wid)

        lay.addLayout(hlay, 0, 0, 1, len(idcs_types))
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 6)
