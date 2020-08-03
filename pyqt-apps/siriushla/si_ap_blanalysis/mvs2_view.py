"""Beam Line MVS2 View."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, \
    QFormLayout
import qtawesome as qta
from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName

from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow, SiriusProcessImage, \
    SiriusSpinbox, PyDMStateButton


class BeamLineMVS2View(SiriusMainWindow):
    """Beam line MVS2 View."""

    def __init__(self, parent=None, prefix=VACA_PREFIX,
                 device_analysis='', device_cam=''):
        super().__init__(parent)
        self._prefix = prefix
        self._device_analysis = SiriusPVName(device_analysis[:-1])
        self._device_cam = device_cam[:-1]
        self._color = get_appropriate_color('ID')
        self._title = self._device_analysis.dev + ' MVS2 Analysis Window'
        self.setWindowTitle(self._title)
        self.setWindowIcon(qta.icon('mdi.camera-control', color=self._color))
        self.setObjectName('IDApp')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>'+self._title+'</h3>', self,
                       alignment=Qt.AlignCenter)

        self._process_image = SiriusProcessImage(
            self, device=self._device_analysis, orientation='H',
            convertion_set=False)

        # IOC control
        self._ld_enbl = QLabel('Start/Stop Acq.: ')
        self._sb_enbl = PyDMStateButton(
            self, self._device_analysis+':MeasureCtrl-Sel')
        self._lb_enbl = PyDMLabel(
            self, self._device_analysis+':MeasureCtrl-Sts')

        self._ld_rate = QLabel('Acq. Rate: ')
        self._sb_rate = SiriusSpinbox(
            self, self._device_analysis+':MeasureRate-SP')
        self._sb_rate.showStepExponent = False
        self._lb_rate = PyDMLabel(
            self, self._device_analysis+':MeasureRate-SP')

        gbox_ctrl = QGroupBox('Analysis Control')
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.setAlignment(Qt.AlignTop)
        lay_ctrl.addWidget(self._ld_enbl, 0, 0)
        lay_ctrl.addWidget(self._sb_enbl, 0, 1)
        lay_ctrl.addWidget(self._lb_enbl, 1, 1)
        lay_ctrl.addWidget(self._ld_rate, 2, 0)
        lay_ctrl.addWidget(self._sb_rate, 2, 1)
        lay_ctrl.addWidget(self._lb_rate, 3, 1)

        # Camera Acquisition Status
        self._ld_acqtime = QLabel('Acquire Time: ')
        self._lb_acqtime = PyDMLabel(
            self, self._device_cam+':cam1:AcquireTime_RBV')
        self._lb_acqtime.showUnits = True
        self._ld_acqperd = QLabel('Acquire Period: ')
        self._lb_acqperd = PyDMLabel(
            self, self._device_cam+':cam1:AcquirePeriod_RBV')
        self._lb_acqperd.showUnits = True
        self._ld_numimgs = QLabel('# Images: ')
        self._lb_numimgs = PyDMLabel(
            self, self._device_cam+':cam1:NumImages_RBV')
        self._ld_imgmode = QLabel('Image Mode: ')
        self._lb_imgmode = PyDMLabel(
            self, self._device_cam+':cam1:ImageMode_RBV')
        self._ld_acqsts = QLabel('Acquire Status: ')
        self._lb_acqsts = PyDMLabel(
            self, self._device_cam+':cam1:Acquire_RBV')
        self._ld_capsts = QLabel('Capture Status: ')
        self._lb_capsts = PyDMLabel(
            self, self._device_cam+':HDF1:Capture_RBV')

        gbox_acqsett = QGroupBox('Camera Acquisition Statuses')
        lay_acqsett = QFormLayout(gbox_acqsett)
        lay_acqsett.addRow(self._ld_acqtime, self._lb_acqtime)
        lay_acqsett.addRow(self._ld_acqperd, self._lb_acqperd)
        lay_acqsett.addRow(self._ld_numimgs, self._lb_numimgs)
        lay_acqsett.addRow(self._ld_imgmode, self._lb_imgmode)
        lay_acqsett.addRow(self._ld_acqsts, self._lb_acqsts)
        lay_acqsett.addRow(self._ld_capsts, self._lb_capsts)

        self.cw = QWidget()
        self.cw.setStyleSheet('PyDMLabel{qproperty-alignment: AlignCenter;}')
        lay = QGridLayout(self.cw)
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addWidget(self._process_image, 1, 0, 2, 1)
        lay.addWidget(gbox_ctrl, 1, 1)
        lay.addWidget(gbox_acqsett, 2, 1)
        lay.setColumnStretch(0, 7)
        lay.setColumnStretch(1, 2)
        self.setCentralWidget(self.cw)
