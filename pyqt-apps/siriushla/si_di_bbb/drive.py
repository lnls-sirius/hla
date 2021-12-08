"""BbB Drive Module."""

import os as _os
from PyQt5.QtWidgets import QHBoxLayout, QWIDGETSIZE_MAX

from qtpy.QtGui import QPixmap, QColor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QSpacerItem
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import PyDMStateButton, SiriusFrame, SiriusLabel

from .util import set_bbb_color
from .custom_widgets import WfmGraph


class BbBSingleDriveSettingsWidget(QWidget):
    """BbB Drive Settings Widget."""

    def __init__(
            self, parent=None, prefix=_vaca_prefix, device='', dr_num=None):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._driver_num = dr_num
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        if self._driver_num is not None:
            self.dev_pref += f':DRIVE{dr_num:d}_'
        else:
            self.dev_pref += f':DRIVE_'
        self._setupUi()

    def _setupUi(self):
        if self._driver_num is None:
            ld_drive = QLabel(
                '<h3>Drive Pattern Generator</h3>', self,
                alignment=Qt.AlignCenter)
        else:
            ld_drive = QWidget(self)
            ld_drive.setLayout(QHBoxLayout())
            labd = QLabel(
                f'<h3>Driver {self._driver_num:d}, NCO BITS: </h3>',
                ld_drive, alignment=Qt.AlignRight)
            labd.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lab = PyDMLabel(
                ld_drive, self.dev_pref+'BITS')
            lab.setStyleSheet('font-size: 13pt; font-weight: bold;')
            lab.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            ld_drive.layout().addStretch()
            ld_drive.layout().addWidget(labd)
            ld_drive.layout().addWidget(lab)
            ld_drive.layout().addStretch()

        ld_amp = QLabel('Amplitude', self)
        sb_amp = PyDMSpinbox(self, self.dev_pref+'AMPL')
        sb_amp.showStepExponent = False

        ld_freq = QLabel('Frequency', self)
        sb_freq = PyDMSpinbox(self, self.dev_pref+'FREQ')
        sb_freq.showStepExponent = False

        ld_wav = QLabel('Waveform', self)
        cb_wav = PyDMEnumComboBox(self, self.dev_pref+'WAVEFORM')

        ld_tmod = QLabel('Time MODulation', self)
        cb_tmod = PyDMStateButton(self, self.dev_pref+'MOD')

        ld_span = QLabel('Span', self)
        sb_span = PyDMSpinbox(self, self.dev_pref+'SPAN')
        sb_span.showStepExponent = False

        ld_perd = QLabel('Period', self)
        sb_perd = PyDMSpinbox(self, self.dev_pref+'PERIOD')
        sb_perd.showStepExponent = False

        ld_patt = QLabel('Drive Pattern', self)
        le_patt = PyDMLineEdit(self, self.dev_pref+'PATTERN')

        lb_actfreq = PyDMLabel(self, self.dev_pref+'FREQ_ACT_STRING')
        lb_actspan = PyDMLabel(self, self.dev_pref+'SPAN_ACT_STRING')
        lb_actperd = PyDMLabel(self, self.dev_pref+'PERIOD_ACT')

        lay = QGridLayout(self)
        lay.addWidget(ld_drive, 0, 1, 1, 3)
        lay.addWidget(ld_tmod, 2, 1)
        lay.addWidget(cb_tmod, 2, 2)
        lay.addWidget(ld_amp, 3, 1)
        lay.addWidget(sb_amp, 3, 2)
        lay.addWidget(ld_freq, 4, 1)
        lay.addWidget(lb_actfreq, 4, 3)
        lay.addWidget(sb_freq, 4, 2)
        lay.addWidget(ld_wav, 5, 1)
        lay.addWidget(cb_wav, 5, 2)
        lay.addWidget(ld_span, 6, 1)
        lay.addWidget(sb_span, 6, 2)
        lay.addWidget(lb_actspan, 6, 3)
        lay.addWidget(ld_perd, 7, 1)
        lay.addWidget(sb_perd, 7, 2)
        lay.addWidget(lb_actperd, 7, 3)
        lay.addWidget(ld_patt, 8, 1)
        lay.addWidget(le_patt, 8, 2, 1, 2)
        lay.addItem(QSpacerItem(1, 10), 9, 1)
        lay.addItem(QSpacerItem(1, 10), 13, 1)
        if self._driver_num in {None, 1}:
            pixmap = QPixmap(_os.path.join(
                _os.path.abspath(_os.path.dirname(__file__)), 'drive.png'))
            il_drive = QLabel(self)
            il_drive.setPixmap(pixmap)
            il_drive.setScaledContents(True)
            lay.addWidget(il_drive, 14, 1, 1, 3, alignment=Qt.AlignCenter)
        else:
            wid = QWidget(self)
            wid.setLayout(QHBoxLayout())
            wid.layout().addStretch()

            propty = f':PHTRK_LOOPCTRL{self._driver_num:d}'
            pv = self._prefix + self._device + propty
            lab = SiriusLabel(self, init_channel=pv)
            lab.enum_strings = ['Tracking Off', 'Tracking On']
            lab.displayFormat = lab.DisplayFormat.String
            frame = SiriusFrame(self, pv, is_float=True)
            frame.borderWidth = 2
            frame.add_widget(lab)
            wid.layout().addWidget(frame)
            wid.layout().addStretch()

            lab = QLabel('Track. Freq: ', self)
            wid.layout().addWidget(lab)
            propty = f':PHTRK_FREQ{self._driver_num:d}'
            pv = self._prefix + self._device + propty
            freq = PyDMLabel(self, init_channel=pv)
            wid.layout().addWidget(freq)
            wid.layout().addStretch()

            lay.addWidget(wid, 14, 1, 1, 3)
        lay.setRowStretch(15, 5)
        lay.setColumnStretch(0, 5)
        lay.setColumnStretch(4, 5)


class BbBDriveSettingsWidget(QWidget):
    """BbB Drive Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = device
        self._setupUi()

    def _setupUi(self):
        self.setLayout(QGridLayout())
        ld_drive = QLabel(
            '<h2>Drive Pattern Generators</h2>',
            self, alignment=Qt.AlignCenter)
        self.layout().addWidget(ld_drive, 0, 0, 1, 5)
        for i in range(3):
            drive = BbBSingleDriveSettingsWidget(
                prefix=self._prefix, device=self._device, dr_num=i)
            self.layout().addWidget(drive, 1, 2*i)
        self.layout().setColumnStretch(1, 2)
        self.layout().setColumnStretch(3, 2)

        dev_pref = self._prefix + self._device
        graph_exct = WfmGraph(self)
        graph_exct.setAutoRangeY(False)
        graph_exct.setYRange(-0.01, 1.08)
        graph_exct.showLegend = True
        graph_exct.axisColor = QColor('black')
        graph_exct.add_scatter_curve(
            ychannel=dev_pref+':DRIVE0_MASK',
            xchannel=dev_pref+':SRAM_XSC',
            name='Drive0', color=QColor('red'))
        graph_exct.add_scatter_curve(
            ychannel=dev_pref+':DRIVE1_MASK',
            xchannel=dev_pref+':SRAM_XSC',
            name='Drive1', color=QColor('magenta'), offset=0.02)
        graph_exct.add_scatter_curve(
            ychannel=dev_pref+':DRIVE2_MASK',
            xchannel=dev_pref+':SRAM_XSC',
            name='Drive2', color=QColor('orange'), offset=0.04)

        self.layout().addWidget(graph_exct, 3, 0, 1, 5)
        self.layout().addItem(QSpacerItem(20, 20), 2, 0)
