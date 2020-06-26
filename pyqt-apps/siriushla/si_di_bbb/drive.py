"""BbB Drive Module."""

import os as _os

from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QSpacerItem, QSizePolicy as QSzPlcy

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix


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
        self._cb_tmod = PyDMEnumComboBox(self, self.dev_pref+':DRIVE_MOD')

        self._ld_span = QLabel('Span', self)
        self._sb_span = PyDMSpinbox(self, self.dev_pref+':DRIVE_SPAN')
        self._sb_span.showStepExponent = False

        self._ld_perd = QLabel('Period', self)
        self._sb_perd = PyDMSpinbox(self, self.dev_pref+':DRIVE_PERIOD')
        self._sb_perd.showStepExponent = False

        self._ld_patt = QLabel('Drive Pattern', self)
        self._le_patt = PyDMLineEdit(self, self.dev_pref+':DRIVE_PATTERN')

        self._ld_actfreq = QLabel('Actual Frequency', self)
        self._lb_actfreq = PyDMLabel(
            self, self.dev_pref+':DRIVE_FREQ_ACT_STRING')

        self._ld_actspan = QLabel('Actual Span', self)
        self._lb_actspan = PyDMLabel(
            self, self.dev_pref+':DRIVE_SPAN_ACT_STRING')

        self._ld_actperd = QLabel('Actual Period', self)
        self._lb_actperd = PyDMLabel(self, self.dev_pref+':DRIVE_PERIOD_ACT')

        pixmap = QPixmap(
            _os.path.join(_os.path.abspath(_os.path.dirname(__file__)),
                          'drive.png'))
        self._il_drive = QLabel(self)
        self._il_drive.setPixmap(pixmap)

        lay = QGridLayout(self)
        lay.addItem(
            QSpacerItem(10, 1, QSzPlcy.MinimumExpanding, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(self._ld_drive, 0, 1, 1, 2)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.Fixed), 1, 1)
        lay.addWidget(self._ld_amp, 2, 1)
        lay.addWidget(self._sb_amp, 2, 2)
        lay.addWidget(self._ld_freq, 3, 1)
        lay.addWidget(self._sb_freq, 3, 2)
        lay.addWidget(self._ld_wav, 4, 1)
        lay.addWidget(self._cb_wav, 4, 2)
        lay.addWidget(self._ld_tmod, 5, 1)
        lay.addWidget(self._cb_tmod, 5, 2)
        lay.addWidget(self._ld_span, 6, 1)
        lay.addWidget(self._sb_span, 6, 2)
        lay.addWidget(self._ld_perd, 7, 1)
        lay.addWidget(self._sb_perd, 7, 2)
        lay.addWidget(self._ld_patt, 8, 1)
        lay.addWidget(self._le_patt, 8, 2)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.Fixed), 9, 1)
        lay.addWidget(self._ld_actfreq, 10, 1)
        lay.addWidget(self._lb_actfreq, 10, 2)
        lay.addWidget(self._ld_actspan, 11, 1)
        lay.addWidget(self._lb_actspan, 11, 2)
        lay.addWidget(self._ld_actperd, 12, 1)
        lay.addWidget(self._lb_actperd, 12, 2)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.Fixed), 13, 1)
        lay.addWidget(self._il_drive, 14, 1, 1, 2, alignment=Qt.AlignCenter)
        lay.addItem(QSpacerItem(10, 10, QSzPlcy.MinimumExpanding,
                                QSzPlcy.MinimumExpanding), 15, 3)
