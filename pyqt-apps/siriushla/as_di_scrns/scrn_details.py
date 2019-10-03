"""SiriusScrnView widget."""

from qtpy.QtWidgets import QGridLayout, QFormLayout, \
    QWidget, QGroupBox, QLabel, QPushButton, QVBoxLayout
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel

from siriuspy.namesys import SiriusPVName

from siriushla import util

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.common.cam_basler import \
    BaslerCamSettings as _BaslerCamSettings
from siriushla.as_di_scrns.scrn_calib import \
    ScrnCalibrationSettings as _ScrnCalibrationSettings


class ScrnSettingsDetails(SiriusMainWindow):
    """Scrn Settings Details Window."""

    def __init__(self, parent=None, device=None, prefix=None):
        """Init."""
        super().__init__(parent=parent)
        self.prefix = SiriusPVName(prefix)
        self.device = SiriusPVName(device)
        self.scrn_prefix = SiriusPVName(prefix+device)
        self.setWindowTitle('Screen Settings Details')
        self.setObjectName(self.scrn_prefix.sec+'App')
        self.centralwidget = QWidget(self)
        self._setupUi()
        self.setCentralWidget(self.centralwidget)

    def _setupUi(self):
        label = QLabel('<h3>'+self.scrn_prefix+' Settings</h3>', self,
                       alignment=Qt.AlignCenter)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_cam = QGroupBox('Camera Settings', self)
        gbox_cam.setLayout(self._setupCamSettingsLayout())

        bt_cal = QPushButton('Screen Calibration', self)
        util.connect_window(bt_cal, _ScrnCalibrationSettings,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QVBoxLayout()
        lay.setSpacing(15)
        lay.addWidget(label)
        lay.addWidget(gbox_general)
        lay.addWidget(gbox_cam)
        lay.addWidget(bt_cal, alignment=Qt.AlignRight)
        self.centralwidget.setLayout(lay)

    def _setupGeneralInfoLayout(self):
        label_MtrPrefix = QLabel('Motor Prefix: ', self)
        self.PyDMLabel_MtrPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':MtrCtrlPrefix-Cte')
        self.PyDMLabel_MtrPrefix.setStyleSheet(
            """max-width:14.20em; max-height:1.29em;""")

        label_CamPrefix = QLabel('Camera Prefix: ', self)
        self.PyDMLabel_CamPrefix = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':CamPrefix-Cte')
        self.PyDMLabel_CamPrefix.setStyleSheet(
            """max-width:14.20em; max-height:1.29em;""")

        flay = QFormLayout()
        flay.addRow(label_MtrPrefix, self.PyDMLabel_MtrPrefix)
        flay.addRow(label_CamPrefix, self.PyDMLabel_CamPrefix)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupCamSettingsLayout(self):
        lay = QGridLayout()
        camdev = self.device.substitute(dev='ScrnCam')
        self._cam_settings = _BaslerCamSettings(self, camdev, self.prefix)
        lay.addWidget(self._cam_settings, 0, 0)
        return lay
