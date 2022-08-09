"""Main module of the Application Interface."""

import enum as _enum
import os as _os
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel, \
    QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from pydm.widgets.display_format import DisplayFormat

import qtawesome as _qta
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState, \
    SiriusLabel, SiriusLedAlert, SiriusLabel
from .details import DeviceParamSettingWindow
from .widgets import DeltaIQPhaseCorrButton, RelativeWidget
from .util import BASIC_INFO
from .chart import ChartWindow
from .motor_control import MotorControlWindow


class DEVICES(_enum.IntEnum):
    """."""

    SHB = (2, 'Sub-harmonic Buncher', 'BUN1', 'SHB')
    Kly1 = (1, 'Klystron 1', 'KLY1', 'K1')
    Kly2 = (0, 'Klystron 2', 'KLY2', 'K2')

    def __new__(cls, value, label, pvname, nickname):
        """."""
        self = int.__new__(cls, value)
        self._value_ = value
        self.label = label
        self.pvname = pvname
        self.nickname = nickname
        return self


class MainWindow(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.display_format = DisplayFormat
        self.main_dev = 'LA-RF:LLRF:'
        self.setObjectName('LIApp')
        self.setWindowTitle('LI LLRF')
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "llrf.png"))
        self.relative_widgets = []
        self._setupui()

    def resizeEvent(self, event):
        """Signal the resize event to the relative Widgets"""
        for relative_item in self.relative_widgets:
            relative_item.relativeResize()

    def buildPvName(self, pv_name, device, pvPrefix='', pvSufix=''):
        """Build the pv name"""
        return (self.prefix + self.main_dev +
            device + ":" + pvPrefix + pv_name + pvSufix)

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_container.setMinimumSize(950, 0)
        return self.image_container

    def formatLabel(self, pv_name='', pv_type='Power'):
        """Get widget type"""
        widget = SiriusLabel(init_channel=pv_name)
        widget.precisionFromPV = False
        widget.precision = 2
        if pv_type == 'Power':
            widget._display_format_type = self.display_format.Exponential
        return widget

    def showChartBtn(self, device, channel, chart_type):
        """Show the Chart Button Widget"""
        widget = QPushButton(chart_type)
        _util.connect_window(
            widget, ChartWindow,
            parent=self, dev=device, chart_type=chart_type, channel=channel)
        widget.setMinimumSize(20, 20)
        return widget

    def baseWidget(
        self, title='', pv_name=''):
            """Show the base widget"""
            """Base Widget: 'title'  'PV information'"""
            bw_hlay = QHBoxLayout()
            bw_hlay.addWidget(
                QLabel(title), alignment=Qt.AlignCenter)

            widget = self.formatLabel(pv_name, title)
            widget.showUnits = True
            bw_hlay.addWidget(
                widget, alignment=Qt.AlignCenter)

            return bw_hlay

    def basicInfoBox(self, device, channel, info):
        """Show the basic information of an element"""
        """
            The basic information of and element consists of:
            -Power and Phase information
            -Chart buttons
        """
        group = QGroupBox()
        bi_vlay = QVBoxLayout()
        bi_vlay.setContentsMargins(2, 2, 2, 2)

        for chart_type in info["Chart"]:
            bi_vlay.addWidget(
                self.showChartBtn(
                    device, channel, chart_type),
                alignment=Qt.AlignCenter)

        for basic_info in ["Power", "Phase"]:
            bi_vlay.addLayout(
                self.baseWidget(
                    basic_info,
                    self.buildPvName(
                        channel, device,
                        "GET_", '_' + basic_info.upper())))
        group.setLayout(bi_vlay)
        group.setStyleSheet('''
            max-width: 160px; max-height: 150px;
        ''')

        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=group,
            relative_pos=info["Position"])
        self.relative_widgets.append(rel_wid)

    def motorControlBtn(self, device, info):
        """Show the motor control button"""
        btn = QPushButton("Motor Control")
        _util.connect_window(
            btn, MotorControlWindow,
            parent=self, motor_type=device)
        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=btn,
            relative_pos=info["Position"])
        self.relative_widgets.append(rel_wid)

    def buildDevicesWidgets(self):
        """Build and arrange the basic information
        and control buttons on the image"""

        for device, channel in BASIC_INFO.items():
            for pv_name, info in channel.items():
                if device != "MOTOR":
                    self.basicInfoBox(device, pv_name, info)
                else:
                    self.motorControlBtn(pv_name, info)

    def _setupui(self):
        """."""
        lay1 = QGridLayout()
        self.setLayout(lay1)

        lay1.addWidget(self.imageViewer(), 0, 1, 3, 10)
        self.buildDevicesWidgets()

        for dev in DEVICES:
            grbox = QGroupBox(dev.label, self)
            lay = QGridLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            grbox.setLayout(lay)
            lay.addWidget(
                ControlBox(
                    grbox, dev.pvname, main_dev=self.main_dev,
                    device=dev, prefix=self.prefix),
                0, 0)
            lay1.addWidget(grbox, dev.value, 0)


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
            device=self.device, prefix=self.main_dev)
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
        if self.dev != DEVICES.SHB:
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
                spa.showStepExponent = False
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
        if self.dev == DEVICES.SHB:
            labc = QLabel('Phase Diff [°]', self)
            rbpv = basename + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            btn = QPushButton("Chart")
            _util.connect_window(
                btn, ChartWindow,
                parent=self, dev=self.dev, chart_type="Diff")
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
