
"""LILLRF Control Widget."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QWidget, QLabel, \
    QHBoxLayout, QPushButton

import enum as _enum
import qtawesome as _qta

from .. import util as _util
from ..widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState, \
    SiriusLabel, SiriusLedAlert
from .details import DeviceParamSettingWindow
from .widgets import DeltaIQPhaseCorrButton
from .chart import ChartWindow


class DEVICES(_enum.IntEnum):
    """."""

    Kly2 = (0, 'Klystron 2', 'KLY2', 'K2')
    Kly1 = (1, 'Klystron 1', 'KLY1', 'K1')
    SHB = (2, 'Sub-harmonic Buncher', 'BUN1', 'SHB')

    def __new__(cls, value, label, pvname, nickname):
        """."""
        self = int.__new__(cls, value)
        self._value_ = value
        self.label = label
        self.pvname = pvname
        self.nickname = nickname
        return self


class ControlBox(QWidget):
    """."""

    def __init__(
        self, parent=None, dev='', main_dev='', device=None, prefix=''):
            """."""
            super().__init__(parent=parent)
            self.prefix = prefix
            self.main_dev = main_dev
            self.dev = dev
            self.device = device
            self._setupui()

    def _setupui(self):
        """."""
        basename = self.prefix + self.main_dev + self.dev

        lay1 = QGridLayout()
        self.setLayout(lay1)

        row = 0
        labb = QLabel('Setpoint', self)
        labc = QLabel('Readback', self)
        lay1.addWidget(labb, row, 1, alignment=Qt.AlignCenter)
        lay1.addWidget(labc, row, 2, alignment=Qt.AlignCenter)

        pb_param = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        pb_param.setToolTip('Open Parameter Setting Window')
        pb_param.setObjectName('detail')
        pb_param.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        _util.connect_window(
            pb_param, DeviceParamSettingWindow, parent=self,
            device=self.device, main_dev=self.main_dev, prefix=self.prefix)
        lay1.addWidget(pb_param, row, 0, alignment=Qt.AlignLeft)

        props = (
            ('State', 'STREAM'), ('Trigger', 'EXTERNAL_TRIGGER_ENABLE'),
            ('Integral', 'INTEGRAL_ENABLE'), ('Feedback', 'FB_MODE'))
        for name, prop in props:
            row += 1
            lab1 = QLabel(name, self)
            sppv = basename + ':SET_' + prop
            rbpv = basename + ':GET_' + prop
            sp1 = PyDMStateButton(self, init_channel=sppv)
            rb1 = SiriusLedState(self, init_channel=rbpv)
            lay1.addWidget(lab1, row, 0)
            lay1.addWidget(sp1, row, 1)
            lay1.addWidget(rb1, row, 2)

        props = [('Amp [%]', 'AMP'), ('Phase [°]', 'PHASE'),
                 ('↳ ΔPhase (IQ Corr)', '')]
        if self.dev != 'BUN1':
            props.append(('Refl. Pow. [MW]', 'REFL_POWER_LIMIT'))
        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            if 'IQ Corr' in name:
                dniqc = DeltaIQPhaseCorrButton(
                    self, self.dev, main_dev=self.main_dev, delta=-90, prefix=self.prefix)
                dpiqc = DeltaIQPhaseCorrButton(
                    self, self.dev, main_dev=self.main_dev, delta=90, prefix=self.prefix)
                lay1.addWidget(laba, row, 0)
                lay1.addWidget(dniqc, row, 1, alignment=Qt.AlignCenter)
                lay1.addWidget(dpiqc, row, 2, alignment=Qt.AlignCenter)
            else:
                sppv = basename + ':SET_' + prop
                rbpv = basename + ':GET_' + prop
                spa = SiriusSpinbox(self, init_channel=sppv)
                spa.precisionFromPV = False
                spa.precision = 2
                rba = SiriusLabel(self, init_channel=rbpv)
                rba.precisionFromPV = False
                rba.precision = 2
                lay1.addWidget(laba, row, 0)
                lay1.addWidget(spa, row, 1)
                lay1.addWidget(rba, row, 2)

        row += 1
        hlay = QHBoxLayout()
        if self.dev == 'BUN1':
            labc = QLabel('Phase Diff [°]', self)
            rbpv = basename + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            btn = QPushButton("Chart")
            _util.connect_window(
                btn, ChartWindow,
                parent=self, dev=self.dev,
                chart_type="Diff", prefix=self.prefix)
            lay1.addWidget(labc, row, 0, 1, 2)
            lay1.addWidget(rbc, row, 1)
            lay1.addWidget(btn, row, 2)
            row += 1
        else:
            rbpv = basename + ':GET_INTERLOCK'
            rb1 = SiriusLedAlert(self, init_channel=rbpv)
            hlay.addWidget(QLabel('Refl. Pow. Intlk'))
            hlay.addWidget(rb1)

        hlay.addStretch()
        rbpv = basename + ':GET_TRIGGER_STATUS'
        rb2 = SiriusLedAlert(self, init_channel=rbpv)
        rb2.setOnColor(rb2.LightGreen)
        rb2.setOffColor(rb2.Red)
        hlay.addWidget(QLabel('Trig. Stts'))
        hlay.addWidget(rb2)
        lay1.addLayout(hlay, row, 0, 1, 3)

        self.setStyleSheet(
            "DeltaIQPhaseCorrButton{max-width: 3em;}")
