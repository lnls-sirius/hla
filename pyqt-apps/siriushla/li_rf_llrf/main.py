"""Main module of the Application Interface."""

import enum as _enum
import os as _os
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel, \
    QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QWidget
from pydm.widgets import PyDMLabel, PyDMSpinbox
import qtawesome as _qta
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..widgets import SiriusMainWindow
from ..widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState, \
    SiriusLabel, SiriusLedAlert
from .details import DeviceParamSettingWindow
from .widgets import DeltaIQPhaseCorrButton, GraphAmpPha, GraphIvsQ, \
    RelativeWidget
from .util import BASIC_INFO


class DEVICES(_enum.IntEnum):
    """."""

    SHB = (0, 'Sub-harmonic Buncher', 'BUN1', 'SHB')
    Kly1 = (1, 'Klystron 1', 'KLY1', 'K1')
    Kly2 = (2, 'Klystron 2', 'KLY2', 'K2')

    def __new__(cls, value, label, pvname, nickname):
        """."""
        self = int.__new__(cls, value)
        self._value_ = value
        self.label = label
        self.pvname = pvname
        self.nickname = nickname
        return self

class MainWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.setObjectName('LIApp')
        self.setWindowTitle('LI LLRF')
        self.setWindowIcon(_qta.icon(
            'mdi.waves', color=_util.get_appropriate_color('LI')))
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "llrf.png"))
        self.relativeWidgets = []

        self._setupui()

    def resizeEvent(self, event):
        for relativeItem in self.relativeWidgets:
            relativeItem.relativeResize(event)

    def buildPvName(self, pv_name, device, prefix='', sufix=''):
        return 'LA-RF:LLRF:' + device + ":" + prefix + pv_name + sufix

    def imageViewer(self):
        ''' Build the image'''
        self.image_container.setPixmap(self.pixmap)
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_container.setMinimumSize(950, 0)
        return self.image_container

    def getWidType(self, wid_type='label', pv_name=''):
        ''' Get widget type '''
        if wid_type == 'spinBox':
            widget = PyDMSpinbox(init_channel=pv_name)
            widget.showStepExponent = False
        elif wid_type == 'label':
            widget = PyDMLabel(init_channel=pv_name)
        return widget

    def showChartBtn(self, chart_type):
        widget = QPushButton(chart_type)
        widget.clicked.connect(
            lambda: print(chart_type))
        widget.setMinimumSize(20, 20)
        return widget

    def baseWidget(self, title='', pv_name='', wid_type='label', hasUnit=False):
        bw_hlay = QHBoxLayout()

        bw_hlay.addWidget(
            QLabel(title), alignment=Qt.AlignCenter)

        widget = self.getWidType(wid_type, pv_name)
        widget.showUnits = hasUnit
        bw_hlay.addWidget(
            widget, alignment=Qt.AlignCenter)

        #Remove
        bw_hlay.addWidget(
            QLabel("um"), alignment=Qt.AlignCenter)

        return bw_hlay

    def basicInfoBox(self, device, channel, info):
        group = QGroupBox()
        bi_vlay = QVBoxLayout()
        bi_vlay.setContentsMargins(5, 5, 5, 5)

        for type_charts in info["Chart"]:
            bi_vlay.addWidget(
                self.showChartBtn(type_charts),
                alignment=Qt.AlignCenter)

        for basicInfo in ["Power", "Phase"]:
            bi_vlay.addLayout(
                self.baseWidget(
                    basicInfo,
                    self.buildPvName(
                        channel, device,
                        "GET_", '_' + basicInfo.upper()),
                    'label', True))
        group.setLayout(bi_vlay)
        group.setStyleSheet('''
            max-width: 160px; max-height: 150px;
        ''')

        relWid = RelativeWidget(
            parent=self.image_container,
            widget=group,
            relativePos=info["Position"])
        self.relativeWidgets.append(relWid)

    def buildDevicesWidgets(self):
        for device, channel in BASIC_INFO.items():
            for pv_name, info in channel.items():
                self.basicInfoBox(device, pv_name, info)

    def _setupui(self):
        """."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay1 = QGridLayout()
        wid.setLayout(lay1)

        lay1.addWidget(self.imageViewer(), 0, 1, 3, 10)
        self.buildDevicesWidgets()

        for dev in DEVICES:
            devSHB = False
            grbox = QGroupBox(dev.label, wid)
            lay = QGridLayout()
            lay.setContentsMargins(10, 10, 10, 10)
            grbox.setLayout(lay)
            if(dev == DEVICES.SHB):
                devSHB = True
            lay.addWidget(
                ControlBox(
                    grbox, dev, prefix=self.prefix, is_shb=devSHB), 0, 0)
            # lay.addWidget(
            #     GraphsWidget(
            #         wid, dev, prefix=self.prefix), 0, 1)
            lay1.addWidget(grbox, dev.value, 0)


class GraphsWidget(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.dev = dev
        self._setupui()

    def _setupui(self):
        """."""
        lay = QGridLayout()
        self.setLayout(lay)

        ivsq = GraphIvsQ(self, self.dev, prefix=self.prefix)
        amp = GraphAmpPha(self, self.dev, prefix=self.prefix)
        pha = GraphAmpPha(self, self.dev, prop='Phase', prefix=self.prefix)

        lay.addWidget(ivsq, 0, 1)
        lay.addWidget(amp, 0, 2)
        lay.addWidget(pha, 0, 3)


class ControlBox(QWidget):
    """."""

    def __init__(self, parent=None, dev=None, prefix='', is_shb=False):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.dev = dev
        self.is_shb = is_shb
        self._setupui()

    def _setupui(self):
        """."""
        basename = self.prefix + ('-' if self.prefix else '') + \
            'LA-RF:LLRF:' + self.dev.pvname

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
            device=self.dev, prefix=self.prefix)
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
        if not self.is_shb:
            props.append(('Refl. Pow. [MW]', 'REFL_POWER_LIMIT'))
        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            if 'IQ Corr' in name:
                dniqc = DeltaIQPhaseCorrButton(
                    self, self.dev, prefix=self.prefix, delta=-90)
                dpiqc = DeltaIQPhaseCorrButton(
                    self, self.dev, prefix=self.prefix, delta=90)
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
        if self.is_shb:
            labc = QLabel('Phase Diff [°]', self)
            rbpv = basename + ':GET_PHASE_DIFF'
            rbc = SiriusLabel(self, init_channel=rbpv)
            rbc.precisionFromPV = False
            rbc.precision = 2
            lay1.addWidget(labc, row, 0, 1, 2)
            lay1.addWidget(rbc, row, 2)
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
