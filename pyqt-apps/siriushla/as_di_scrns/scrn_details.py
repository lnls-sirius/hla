"""SiriusScrnView widget."""

from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QFormLayout, \
                           QSpacerItem, QWidget, QGroupBox, QLabel, \
                           QPushButton, QSizePolicy as QSzPlcy
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel
from siriushla.widgets.windows import SiriusMainWindow, \
                                      create_window_from_widget
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed
from siriushla.as_di_scrns.base import \
    create_propty_layout as _create_propty_layout
from siriushla.as_di_scrns.scrn_calib import \
    ScrnCalibrationSettings as _ScrnCalibrationSettings


class ScrnSettingsDetails(SiriusMainWindow):
    """Scrn Settings Details Window."""

    def __init__(self, parent=None, device=None, prefix=None):
        """Init."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = self.prefix+self.device
        self.setWindowTitle('Screen Settings Details')
        self.centralwidget = QWidget(self)
        self._setupUi()
        self.setCentralWidget(self.centralwidget)

    def _setupUi(self):
        label = QLabel('<h3>'+self.scrn_prefix+' Settings</h3>', self,
                       alignment=Qt.AlignCenter)

        gbox_general = QGroupBox('Low Level Devices Prefixes', self)
        gbox_general.setLayout(self._setupGeneralInfoLayout())

        gbox_acq = QGroupBox('Camera Acquire Settings', self)
        gbox_acq.setLayout(self._setupCamAcqSettingsLayout())

        gbox_trg = QGroupBox('Screen Trigger', self)
        gbox_trg.setLayout(self._setupScrnTriggerLayout())

        gbox_ROI = QGroupBox('Camera Region of Interest (ROI) Settings', self)
        gbox_ROI.setLayout(self._setupROISettingsLayout())

        gbox_err = QGroupBox('Camera Errors Monitoring', self)
        gbox_err.setLayout(self._setupErrorMonLayout())

        bt_cal = QPushButton('Screen Calibration', self)
        util.connect_window(bt_cal, _ScrnCalibrationSettings,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QGridLayout()
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 1, 0)
        lay.addWidget(gbox_general, 2, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 3, 0)
        lay.addWidget(gbox_acq, 4, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 5, 0)
        lay.addWidget(gbox_trg, 6, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 7, 0)
        lay.addWidget(gbox_ROI, 8, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 9, 0)
        lay.addWidget(gbox_err, 10, 0, 1, 2)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 11, 0)
        lay.addWidget(bt_cal, 12, 1)
        lay.addItem(QSpacerItem(
            40, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 13, 0)
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

    def _setupCamAcqSettingsLayout(self):
        label_CamEnbl = QLabel('Acquire Enable Status: ', self)
        hbox_CamEnbl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamEnbl',
            propty_type='enbldisabl')

        label_AcqMode = QLabel('Acquire Mode: ', self)
        hbox_AcqMode = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqMode',
            propty_type='enum')

        label_AcqPeriod = QLabel('Acquire Period [s]: ', self)
        hbox_AcqPeriod = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamAcqPeriod',
            propty_type='sprb')

        label_ExpMode = QLabel('Exposure Mode: ', self)
        hbox_ExpMode = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureMode',
            propty_type='enum')

        label_ExpTime = QLabel('Exposure Time [us]: ', self)
        hbox_ExpTime = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamExposureTime',
            propty_type='sprb')

        label_Gain = QLabel('Gain [dB]: ', self)
        hbox_Gain = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamGain',
            propty_type='sprb', cmd={'label': 'Auto Gain',
                                     'pressValue': 1,
                                     'name': 'CamAutoGain'})

        label_BlackLevel = QLabel('Black Level: ', self)
        hbox_BlackLevel = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamBlackLevel',
            propty_type='sprb')

        flay = QFormLayout()
        flay.addRow(label_CamEnbl, hbox_CamEnbl)
        flay.addRow(label_AcqMode, hbox_AcqMode)
        flay.addRow(label_AcqPeriod, hbox_AcqPeriod)
        flay.addRow(label_ExpMode, hbox_ExpMode)
        flay.addRow(label_ExpTime, hbox_ExpTime)
        flay.addRow(label_Gain, hbox_Gain)
        flay.addRow(label_BlackLevel, hbox_BlackLevel)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupScrnTriggerLayout(self):
        if 'TB' in self.device:
            trg_prefix = self.prefix+'TB-Fam:TI-Scrn'
        elif 'BO' in self.device:
            trg_prefix = self.prefix+'BO-Fam:TI-Scrn'
        elif 'TS' in self.device:
            trg_prefix = self.prefix+'TS-Fam:TI-Scrn'

        l_TIstatus = QLabel('Status: ', self)
        self.ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self, channels2values={trg_prefix+':State-Sts': 1,
                                          trg_prefix+':Status-Mon': 0})
        self.ledmulti_TIStatus.setStyleSheet("""
            min-width:7.10em;\nmax-width:7.10em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.pb_trgdetails = QPushButton('Open details', self)
        self.pb_trgdetails.setStyleSheet("""
            min-width:7.10em;\nmax-width:7.10em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        trg_w = create_window_from_widget(HLTriggerDetailed, is_main=True)
        util.connect_window(self.pb_trgdetails, trg_w, parent=self,
                            prefix=trg_prefix)
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(self.ledmulti_TIStatus)
        hlay_TIstatus.addWidget(self.pb_trgdetails)

        l_TIdelay = QLabel('Delay [us]: ', self)
        hlay_TIdelay = _create_propty_layout(
            parent=self, prefix=trg_prefix, propty='Delay',
            propty_type='sprb')

        flay = QFormLayout()
        flay.addRow(l_TIstatus, hlay_TIstatus)
        flay.addRow(l_TIdelay, hlay_TIdelay)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        return flay

    def _setupROISettingsLayout(self):
        label_ImgMaxWidth = QLabel('Maximum Width [pixels]: ', self)
        self.PyDMLabel_ImgMaxWidth = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxWidth-Cte')
        self.PyDMLabel_ImgMaxWidth.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_ImgMaxHeight = QLabel('Maximum Height [pixels]: ', self)
        self.PyDMLabel_ImgMaxHeight = PyDMLabel(
            parent=self, init_channel=self.scrn_prefix+':ImgMaxHeight-Cte')
        self.PyDMLabel_ImgMaxHeight.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_ROIWidth = QLabel('Width [pixels]: ', self)
        hbox_ROIWidth = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIWidth',
            propty_type='sprb')

        label_ROIHeight = QLabel('Heigth [pixels]: ', self)
        hbox_ROIHeight = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIHeight',
            propty_type='sprb')

        label_ROIOffsetX = QLabel('Offset X [pixels]: ', self)
        hbox_ROIOffsetX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetX',
            propty_type='sprb')

        label_ROIOffsetY = QLabel('Offset Y [pixels]: ', self)
        hbox_ROIOffsetY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIOffsetY',
            propty_type='sprb')

        label_AutoCenterX = QLabel('Auto Center X: ', self)
        hbox_AutoCenterX = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIAutoCenterX',
            propty_type='offon')

        label_AutoCenterY = QLabel('Auto Center Y: ', self)
        hbox_AutoCenterY = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgROIAutoCenterY',
            propty_type='offon')

        flay = QFormLayout()
        flay.addRow(label_ImgMaxWidth, self.PyDMLabel_ImgMaxWidth)
        flay.addRow(label_ImgMaxHeight, self.PyDMLabel_ImgMaxHeight)
        flay.addRow(label_ROIWidth, hbox_ROIWidth)
        flay.addRow(label_ROIHeight, hbox_ROIHeight)
        flay.addRow(label_ROIOffsetX, hbox_ROIOffsetX)
        flay.addRow(label_ROIOffsetY, hbox_ROIOffsetY)
        flay.addRow(label_AutoCenterX, hbox_AutoCenterX)
        flay.addRow(label_AutoCenterY, hbox_AutoCenterY)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        return flay

    def _setupErrorMonLayout(self):
        label_CamTemp = QLabel('Temperature State: ', self)
        hbox_CamTempState = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamTempState',
            propty_type='mon')

        label_LastErr = QLabel('Last Error: ', self)
        hbox_LastErr = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CamLastErr',
            propty_type='mon', cmd={'label': 'Clear Last Error',
                                    'pressValue': 1,
                                    'name': 'CamClearLastErr'})

        flay = QFormLayout()
        flay.addRow(label_CamTemp, hbox_CamTempState)
        flay.addRow(label_LastErr, hbox_LastErr)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay
