"""Main window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QGridLayout, QSizePolicy as QSzPlcy, \
    QWidget

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.idff.csdev import IDFFConst

from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusLabel, SiriusSpinbox, \
    PyDMStateButton, SiriusLedState, PyDMLogLabel
from .custom_widgets import ConfigLineEdit


class IDFFWindow(SiriusMainWindow):
    """ID FF main window."""

    def __init__(self, parent=None, prefix='', idname=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix or _VACA_PREFIX
        self.idname = idname
        self._const = IDFFConst(idname)
        self.device = _PVName(self._const.idffname)
        self.dev_pref = self.device.substitute(prefix=prefix)
        self.setObjectName('IDApp')
        self.setWindowTitle(self.device)
        self.setWindowIcon(  # TODO update
            qta.icon('mdi.circle', color=get_appropriate_color('ID')))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.title = QLabel('<h3>'+self.device+'</h3>',
                            alignment=Qt.AlignCenter)

        ld_configname = QLabel(
            'Config. Name', self, alignment=Qt.AlignRight)
        self.le_configname = ConfigLineEdit(
            self, self.dev_pref.substitute(propty='ConfigName-SP'))
        self.le_configname.setStyleSheet('min-width:10em; max-width:10em;')
        self.lb_configname = SiriusLabel(
            self, self.dev_pref.substitute(propty='ConfigName-RB'))

        ld_loopstate = QLabel(
            'Loop State', self, alignment=Qt.AlignRight)
        self.sb_loopstate = PyDMStateButton(
            self, self.dev_pref.substitute(propty='LoopState-Sel'))
        self.lb_loopstate = SiriusLedState(
            self, self.dev_pref.substitute(propty='LoopState-Sts'))

        ld_loopfreq = QLabel(
            'Loop Freq.', self, alignment=Qt.AlignRight)
        self.sb_loopfreq = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='LoopFreq-SP'))
        self.lb_loopfreq = SiriusLabel(
            self, self.dev_pref.substitute(propty='LoopFreq-RB'))

        ld_polar = QLabel(
            'Polarization', self, alignment=Qt.AlignRight)
        self.lb_polar = SiriusLabel(
            self, self.dev_pref.substitute(propty='Polarization-Mon'))

        self.log = PyDMLogLabel(
            self, init_channel=self.dev_pref.substitute(propty='Log-Mon'))
        self.log.setSizePolicy(
            QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding)
        self.log.setAlternatingRowColors(True)
        self.log.maxCount = 2000

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0)
        lay.addWidget(ld_configname, 1, 0)
        lay.addWidget(self.le_configname, 1, 1)
        lay.addWidget(self.lb_configname, 1, 2)
        lay.addWidget(ld_loopstate, 2, 0)
        lay.addWidget(self.sb_loopstate, 2, 1)
        lay.addWidget(self.lb_loopstate, 2, 2)
        lay.addWidget(ld_loopfreq, 3, 0)
        lay.addWidget(self.sb_loopfreq, 3, 1)
        lay.addWidget(self.lb_loopfreq, 3, 2)
        lay.addWidget(ld_polar, 4, 0)
        lay.addWidget(self.lb_polar, 4, 1)
        lay.addWidget(self.log, 5, 0, 1, 3)
        self.setCentralWidget(wid)
