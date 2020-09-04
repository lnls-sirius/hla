"""BbB Drive Module."""

import os as _os

from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QSpacerItem, QSizePolicy as QSzPlcy

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit
from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..widgets import PyDMStateButton

class BbBDriveSettingsWidget(QWidget):
    """BbB Drive Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_drive = QLabel(
            '<h3>Drive Pattern Generator</h3>',
            self, alignment=Qt.AlignCenter)

        self._ld_amp = QLabel('Amplitude', self)
        self._sb_amp = PyDMSpinbox(self, self.dev_pref+':DRIVE_AMPL')
        self._sb_amp.showStepExponent = False

        self._ld_freq = QLabel('Frequency', self)
        self._sb_freq = PyDMSpinbox(self, self.dev_pref+':DRIVE_FREQ')
        self._sb_freq.showStepExponent = False

        self._ld_wav = QLabel('Waveform', self)
        self._cb_wav = PyDMEnumComboBox(self, self.dev_pref+':DRIVE_WAVEFORM')

        self._ld_tmod = QLabel('TMOD', self)
        self._cb_tmod = PyDMStateButton(self, self.dev_pref+':DRIVE_MOD')

        self._ld_span = QLabel('Span', self)
        self._sb_span = PyDMSpinbox(self, self.dev_pref+':DRIVE_SPAN')
        self._sb_span.showStepExponent = False

        self._ld_perd = QLabel('Period', self)
        self._sb_perd = PyDMSpinbox(self, self.dev_pref+':DRIVE_PERIOD')
        self._sb_perd.showStepExponent = False

        self._ld_patt = QLabel('Drive Pattern', self)
        self._le_patt = PyDMLineEdit(self, self.dev_pref+':DRIVE_PATTERN')

        self._lb_actfreq = PyDMLabel(
            self, self.dev_pref+':DRIVE_FREQ_ACT_STRING')
        self._lb_actspan = PyDMLabel(
            self, self.dev_pref+':DRIVE_SPAN_ACT_STRING')
        self._lb_actperd = PyDMLabel(self, self.dev_pref+':DRIVE_PERIOD_ACT')

        pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), 'drive.png'))
        self._il_drive = QLabel(self)
        self._il_drive.setPixmap(pixmap)
        self._il_drive.setScaledContents(True)

        lay = QGridLayout(self)
        lay.addWidget(self._ld_drive, 0, 1, 1, 3)
        lay.addWidget(self._ld_tmod, 2, 1)
        lay.addWidget(self._cb_tmod, 2, 2)
        lay.addWidget(self._ld_amp, 3, 1)
        lay.addWidget(self._sb_amp, 3, 2)
        lay.addWidget(self._ld_freq, 4, 1)
        lay.addWidget(self._lb_actfreq, 4, 3)
        lay.addWidget(self._sb_freq, 4, 2)
        lay.addWidget(self._ld_wav, 5, 1)
        lay.addWidget(self._cb_wav, 5, 2)
        lay.addWidget(self._ld_span, 6, 1)
        lay.addWidget(self._sb_span, 6, 2)
        lay.addWidget(self._lb_actspan, 6, 3)
        lay.addWidget(self._ld_perd, 7, 1)
        lay.addWidget(self._sb_perd, 7, 2)
        lay.addWidget(self._lb_actperd, 7, 3)
        lay.addWidget(self._ld_patt, 8, 1)
        lay.addWidget(self._le_patt, 8, 2, 1, 2)
        lay.addItem(QSpacerItem(1, 10), 9, 1)
        lay.addItem(QSpacerItem(1, 10), 13, 1)
        lay.addWidget(self._il_drive, 14, 1, 1, 3, alignment=Qt.AlignCenter)
        lay.setRowStretch(15, 5)
        lay.setColumnStretch(0, 5)
        lay.setColumnStretch(4, 5)
