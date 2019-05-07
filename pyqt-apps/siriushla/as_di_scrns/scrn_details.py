"""SiriusScrnView widget."""

from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QFormLayout, \
                           QWidget, QGroupBox, QLabel, QPushButton
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel

from siriuspy.namesys import SiriusPVName

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

        gbox_bg = QGroupBox('Background Acquisition', self)
        gbox_bg.setLayout(self._setupBGAcqLayout())

        gbox_intensity = QGroupBox('Image Intensity Settings', self)
        gbox_intensity.setLayout(self._setupImgIntensityLayout())

        gbox_err = QGroupBox('Camera Errors Monitoring', self)
        gbox_err.setLayout(self._setupErrorMonLayout())

        bt_cal = QPushButton('Screen Calibration', self)
        util.connect_window(bt_cal, _ScrnCalibrationSettings,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.setHorizontalSpacing(15)
        lay.addWidget(label, 0, 0, 1, 3)
        lay.addWidget(gbox_general, 1, 0, 1, 1)
        lay.addWidget(gbox_acq, 2, 0, 2, 1)
        lay.addWidget(gbox_trg, 4, 0, 1, 1)
        lay.addWidget(gbox_err, 5, 0, 1, 1)
        lay.addWidget(gbox_ROI, 1, 1, 2, 2)
        lay.addWidget(gbox_bg, 3, 1, 1, 2)
        lay.addWidget(gbox_intensity, 4, 1, 2, 2)
        lay.addWidget(bt_cal, 6, 2)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 6)
        lay.setRowStretch(3, 3)
        lay.setRowStretch(4, 2)
        lay.setRowStretch(5, 3)
        lay.setRowStretch(6, 1)
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
        if 'TB' in self.device or 'BO' in self.device:
            trg_prefix = self.prefix+'AS-Fam:TI-Scrn-TBBO'
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
        trg_w = create_window_from_widget(
            HLTriggerDetailed, title=trg_prefix+' Detailed Settings',
            is_main=True)
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
        flay.setFormAlignment(Qt.AlignCenter)
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

    def _setupBGAcqLayout(self):
        label_EnblBG = QLabel('Enable subtraction: ', self)
        hbox_EnblBG = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix,
            propty='ImgEnblBGSubtraction', propty_type='enbldisabl')

        label_SaveBG = QLabel('Save BG: ', self)
        hbox_SaveBG = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgSaveBG',
            cmd={'label': 'Save', 'pressValue': 1, 'name': 'ImgSaveBG'})

        label_ValidBG = QLabel('Is valid BG? ', self)
        hbox_ValidBG = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgValidBG',
            propty_type='mon')

        flay = QFormLayout()
        flay.addRow(label_EnblBG, hbox_EnblBG)
        flay.addRow(label_SaveBG, hbox_SaveBG)
        flay.addRow(label_ValidBG, hbox_ValidBG)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay

    def _setupImgIntensityLayout(self):
        label_EnblAdjust = QLabel('Enable Scale and Offset Adjust:', self)
        hbox_EnblAdjust = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgEnblOffsetScale',
            propty_type='enbldisabl')

        label_AutoAdjust = QLabel('Automatic Intensity Adjust:', self)
        hbox_AutoAdjust = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgAutoOffsetScale',
            cmd={'label': 'Auto Adjust', 'pressValue': 1,
                 'name': 'ImgAutoOffsetScale'})

        label_PixelScale = QLabel('Pixel Scale:', self)
        hbox_PixelScale = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgPixelScale',
            propty_type='sprb', use_linedit=True)

        label_PixelOffset = QLabel('Pixel Offset:', self)
        hbox_PixelOffset = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgPixelOffset',
            propty_type='sprb', use_linedit=True)

        label_EnblLowClip = QLabel('Enable Low Cliping: ', self)
        hbox_EnblLowClip = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgEnblLowClip',
            propty_type='enbldisabl')

        label_LowClip = QLabel('Minimum Intensity for Low Cliping: ', self)
        hbox_LowClip = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgLowClip',
            propty_type='sprb', use_linedit=True)

        label_EnblHighClip = QLabel('Enable High Cliping: ', self)
        hbox_EnblHighClip = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgEnblHighClip',
            propty_type='enbldisabl')

        label_HighClip = QLabel('Maximum Intensity for High Cliping: ', self)
        hbox_HighClip = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='ImgHighClip',
            propty_type='sprb', use_linedit=True)

        flay = QFormLayout()
        flay.addRow(label_EnblAdjust, hbox_EnblAdjust)
        flay.addRow(label_AutoAdjust, hbox_AutoAdjust)
        flay.addRow(label_PixelScale, hbox_PixelScale)
        flay.addRow(label_PixelOffset, hbox_PixelOffset)
        flay.addRow(label_EnblLowClip, hbox_EnblLowClip)
        flay.addRow(label_LowClip, hbox_LowClip)
        flay.addRow(label_EnblHighClip, hbox_EnblHighClip)
        flay.addRow(label_HighClip, hbox_HighClip)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
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

        cam_prefix = SiriusPVName(self.scrn_prefix).substitute(dev='ScrnCam')
        label_Reset = QLabel('Reset Screen: ', self)
        hbox_Reset = _create_propty_layout(
            parent=self, prefix=cam_prefix, propty='Reset',
            cmd={'label': 'Reset', 'pressValue': 1, 'name': 'Rst'})

        flay = QFormLayout()
        flay.addRow(label_CamTemp, hbox_CamTempState)
        flay.addRow(label_LastErr, hbox_LastErr)
        flay.addRow(label_Reset, hbox_Reset)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        return flay
