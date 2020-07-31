"""Beam Line MVS2 View."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, \
    QSpacerItem, QSizePolicy as QSzPlcy
import qtawesome as qta
from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName

from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow, SiriusProcessImage


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

        self._process_image = SiriusProcessImage(self, self._device_analysis)

        self._ld_acqtime = QLabel('Acquire Time: ')
        self._lb_acqtime = PyDMLabel(
            self, self._device_cam+':cam1:AcquireTime')
        self._ld_acqperd = QLabel('Acquire Period: ')
        self._lb_acqperd = PyDMLabel(
            self, self._device_cam+':cam1:AcquirePeriod')
        self._ld_numimgs = QLabel('# Images: ')
        self._lb_numimgs = PyDMLabel(
            self, self._device_cam+':cam1:NumImages')
        self._ld_imgmode = QLabel('Image Mode: ')
        self._lb_imgmode = PyDMLabel(
            self, self._device_cam+':cam1:ImageMode')
        self._ld_acqsts = QLabel('Acquire Status: ')
        self._lb_acqsts = PyDMLabel(
            self, self._device_cam+':cam1:Acquire')
        self._ld_capsts = QLabel('Capture Status: ')
        self._lb_capsts = PyDMLabel(
            self, self._device_cam+':HDF1:Capture')

        gbox_acqsett = QGroupBox('Acquisition Settings')
        lay_acqsett = QGridLayout(gbox_acqsett)
        lay_acqsett.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 0)
        lay_acqsett.addWidget(self._ld_acqtime, 0, 1)
        lay_acqsett.addWidget(self._lb_acqtime, 0, 2)
        lay_acqsett.addWidget(self._ld_acqperd, 1, 1)
        lay_acqsett.addWidget(self._lb_acqperd, 1, 2)
        lay_acqsett.addWidget(self._ld_numimgs, 2, 1)
        lay_acqsett.addWidget(self._lb_numimgs, 2, 2)
        lay_acqsett.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 3)
        lay_acqsett.addWidget(self._ld_imgmode, 0, 4)
        lay_acqsett.addWidget(self._lb_imgmode, 0, 5)
        lay_acqsett.addWidget(self._ld_acqsts, 1, 4)
        lay_acqsett.addWidget(self._lb_acqsts, 1, 5)
        lay_acqsett.addWidget(self._ld_capsts, 2, 4)
        lay_acqsett.addWidget(self._lb_capsts, 2, 5)
        lay_acqsett.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 6)

        self.cw = QWidget()
        self.cw.setStyleSheet('PyDMLabel{qproperty-alignment: AlignCenter;}')
        lay = QGridLayout(self.cw)
        lay.addWidget(label, 0, 0)
        lay.addWidget(self._process_image, 1, 0)
        lay.addWidget(gbox_acqsett, 2, 0)
        self.setCentralWidget(self.cw)
