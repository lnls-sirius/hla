from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QTabWidget, QLabel, QFormLayout, \
    QHBoxLayout, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName
from siriushla import util
from siriushla.widgets import SiriusLedAlert, SiriusLabel
from siriushla.widgets.windows import create_window_from_widget
from .base import create_propty_layout


class BaslerCamSettings(QTabWidget):

    def __init__(self, parent=None, device='', prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(device).substitute(prefix=prefix)
        self.cam_prefix = self.device.substitute(prefix=prefix)
        self.setObjectName(self.device.sec + 'App')
        self._setupUi()

    def _setupUi(self):
        self.addTab(self._infoWidget(), 'Gen. Info')
        self.addTab(self._statusWidget(), 'Status')
        self.addTab(self._acquisitionWidget(), 'Acquisition')
        self.addTab(self._imgIntesityAndBGWidget(), 'Intensity and BG')
        self.addTab(self._ROIWidget(), 'ROI')
        self.setCurrentIndex(2)
        self.setStyleSheet(
            '#'+self.device.sec+'App{min-width: 31em; max-width: 31em;}')

    def _infoWidget(self):
        label_DevID = QLabel('Device ID:', self)
        hbox_DevID = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='DeviceID', propty_type='cte')
        hbox_DevID.setAlignment(Qt.AlignLeft)

        label_DevVers = QLabel('Device Version:', self)
        hbox_DevVers = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='DeviceVersion', propty_type='cte')
        hbox_DevVers.setAlignment(Qt.AlignLeft)

        label_DevModelName = QLabel('Device Model Name:', self)
        hbox_DevModelName = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='DeviceModelName', propty_type='cte')
        hbox_DevModelName.setAlignment(Qt.AlignLeft)

        label_DevVendorName = QLabel('Device Vendor Name:', self)
        hbox_DevVendorName = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='DeviceVendorName', propty_type='cte')
        hbox_DevVendorName.setAlignment(Qt.AlignLeft)

        label_DevFirmVers = QLabel('Firmware Version:', self)
        hbox_DevFirmVers = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='DeviceFirmwareVersion', propty_type='cte')
        hbox_DevFirmVers.setAlignment(Qt.AlignLeft)

        label_SensorHeight = QLabel('Sensor Height [pixels]:', self)
        hbox_SensorHeight = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='SensorHeight', propty_type='cte')
        hbox_SensorHeight.setAlignment(Qt.AlignLeft)

        label_SensorWidth = QLabel('Sensor Width [pixels]:', self)
        hbox_SensorWidth = create_propty_layout(
            parent=self, prefix=self.cam_prefix, width=15,
            propty='SensorWidth', propty_type='cte')
        hbox_SensorWidth.setAlignment(Qt.AlignLeft)

        wid = QWidget()
        flay = QFormLayout(wid)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label_DevID, hbox_DevID)
        flay.addRow(label_DevVers, hbox_DevVers)
        flay.addRow(label_DevModelName, hbox_DevModelName)
        flay.addRow(label_DevVendorName, hbox_DevVendorName)
        flay.addRow(label_DevFirmVers, hbox_DevFirmVers)
        flay.addRow(label_SensorHeight, hbox_SensorHeight)
        flay.addRow(label_SensorWidth, hbox_SensorWidth)
        return wid

    def _statusWidget(self):
        label_Conn = QLabel('Connection:', self)
        hbox_Conn = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Connection', propty_type='mon')

        label_Temp = QLabel('Temperature State:', self)
        self.lb_Temp = SiriusLabel(
            self, self.cam_prefix.substitute(propty='Temp-Mon'))
        self.lb_Temp.setStyleSheet('min-width:7.1em; max-width:7.1em;')
        self.lb_Temp.setAlignment(Qt.AlignCenter)
        self.led_TempState = SiriusLedAlert(
            self, self.cam_prefix.substitute(propty='TempState-Mon'))
        self.led_TempState.setStyleSheet('min-width:1.29em; max-width:1.29em;')
        self.lb_TempState = SiriusLabel(
            self, self.cam_prefix.substitute(propty='TempState-Mon'))
        self.lb_TempState.setStyleSheet('min-width:2.5em; max-width:2.5em;')
        hbox_Temp = QHBoxLayout()
        hbox_Temp.addWidget(self.lb_Temp)
        hbox_Temp.addWidget(self.led_TempState)
        hbox_Temp.addWidget(self.lb_TempState)

        label_LastErr = QLabel('Last Error:', self)
        hbox_LastErr = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='LastErr', propty_type='mon',
            cmd={'label': 'Clear Last Error', 'pressValue': 1,
                 'name': 'ClearLastErr'})

        label_Reset = QLabel('Reset Camera:', self)
        self.pb_dtl = PyDMPushButton(
            label='', icon=qta.icon('fa5s.sync'),
            parent=self, pressValue=1,
            init_channel=self.cam_prefix.substitute(propty='Rst-Cmd'))
        self.pb_dtl.setObjectName('reset')
        self.pb_dtl.setStyleSheet(
            "#reset{min-width:25px; max-width:25px; icon-size:20px;}")

        wid = QWidget()
        flay = QFormLayout(wid)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label_Conn, hbox_Conn)
        flay.addRow(label_Temp, hbox_Temp)
        flay.addRow(label_LastErr, hbox_LastErr)
        flay.addRow(label_Reset, self.pb_dtl)
        return wid

    def _acquisitionWidget(self):
        label_CamEnbl = QLabel('Acquire Enable Status:', self)
        hbox_CamEnbl = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Enbl', propty_type='enbldisabl')

        label_FrameCnt = QLabel('Frame Count:', self)
        hbox_FrameCnt = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='FrameCnt', propty_type='mon')

        label_AcqMode = QLabel('Acquire Mode:', self)
        hbox_AcqMode = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AcqMode', propty_type='enum')

        label_AcqPeriod = QLabel('Acquire Period [s]:', self)
        hbox_AcqPeriod = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AcqPeriod', propty_type='sprb')

        label_AcqPeriodLowLim = QLabel('Acquire Period Low Limit [s]:', self)
        hbox_AcqPeriodLowLim = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AcqPeriodLowLim', propty_type='sprb')

        label_ExpMode = QLabel('Exposure Mode:', self)
        hbox_ExpMode = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ExposureMode', propty_type='enum')

        label_ExpTime = QLabel('Exposure Time [us]:', self)
        hbox_ExpTime = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ExposureTime', propty_type='sprb')

        label_Gain = QLabel('Gain [dB]:', self)
        hbox_Gain = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Gain', propty_type='sprb',
            cmd={'label': '', 'pressValue': 1, 'width': '25', 'height': '25',
                 'icon': qta.icon('mdi.auto-fix'), 'icon-size': '20',
                 'toolTip': 'Auto Gain', 'name': 'AutoGain'})

        label_TransformType = QLabel('Transform Type:', self)
        hbox_TransformType = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='TransformType', propty_type='enum')

        label_BlackLevel = QLabel('Black Level [gray va]:', self)
        hbox_BlackLevel = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='BlackLevel', propty_type='sprb')

        label_DebouncerPeriod = QLabel('Debouncer Period [us]:', self)
        hbox_DebouncerPeriod = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='DebouncerPeriod', propty_type='sprb')

        self.pb_advanced = QPushButton('Advanced', self)
        my_window = create_window_from_widget(
            BaslerCamAcqAdvSettings, is_main=False,
            title='Basler Camera Advanced Acquisition Settings')
        util.connect_window(self.pb_advanced, my_window, parent=self,
                            device=self.device, prefix=self.prefix)
        hbox_adv = QHBoxLayout()
        hbox_adv.addWidget(self.pb_advanced, alignment=Qt.AlignRight)

        wid = QWidget()
        flay = QFormLayout(wid)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label_CamEnbl, hbox_CamEnbl)
        flay.addRow(label_FrameCnt, hbox_FrameCnt)
        flay.addRow(label_AcqMode, hbox_AcqMode)
        flay.addRow(label_AcqPeriod, hbox_AcqPeriod)
        flay.addRow(label_AcqPeriodLowLim, hbox_AcqPeriodLowLim)
        flay.addRow(label_ExpMode, hbox_ExpMode)
        flay.addRow(label_ExpTime, hbox_ExpTime)
        flay.addRow(label_Gain, hbox_Gain)
        flay.addRow(label_BlackLevel, hbox_BlackLevel)
        flay.addRow(label_DebouncerPeriod, hbox_DebouncerPeriod)
        flay.addRow(label_TransformType, hbox_TransformType)
        flay.addRow(hbox_adv)
        return wid

    def _imgIntesityAndBGWidget(self):
        label_EnblAdjust = QLabel('Enable Scale and Offset Adjust:', self)
        hbox_EnblAdjust = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='EnblOffsetScale', propty_type='enbldisabl')

        label_AutoAdjust = QLabel('Automatic Intensity Adjust:', self)
        hbox_AutoAdjust = create_propty_layout(
            parent=self, prefix=self.cam_prefix, propty='AutoOffsetScale',
            cmd={'label': 'Auto Adjust', 'pressValue': 1,
                 'name': 'AutoOffsetScale'})

        label_PixelScale = QLabel('Pixel Scale:', self)
        hbox_PixelScale = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='PixelScale', propty_type='sprb', use_linedit=True)

        label_PixelOffset = QLabel('Pixel Offset:', self)
        hbox_PixelOffset = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='PixelOffset', propty_type='sprb', use_linedit=True)

        label_EnblLowClip = QLabel('Enable Low Cliping:', self)
        hbox_EnblLowClip = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='EnblLowClip', propty_type='enbldisabl')

        label_LowClip = QLabel('Minimum Intensity for Low Cliping:', self)
        hbox_LowClip = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='LowClip', propty_type='sprb', use_linedit=True)

        label_EnblHighClip = QLabel('Enable High Cliping:', self)
        hbox_EnblHighClip = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='EnblHighClip', propty_type='enbldisabl')

        label_HighClip = QLabel('Maximum Intensity for High Cliping:', self)
        hbox_HighClip = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='HighClip', propty_type='sprb', use_linedit=True)

        label_EnblBG = QLabel('Enable BG Subtraction:', self)
        hbox_EnblBG = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='EnblBGSubtraction', propty_type='enbldisabl')

        label_SaveBG = QLabel('Save BG:', self)
        hbox_SaveBG = create_propty_layout(
            parent=self, prefix=self.cam_prefix, propty='SaveBG',
            cmd={'label': 'Save', 'pressValue': 1, 'name': 'SaveBG'})

        label_ValidBG = QLabel('Is valid BG?', self)
        hbox_ValidBG = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ValidBG', propty_type='mon')

        wid = QWidget()
        flay = QFormLayout(wid)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label_EnblAdjust, hbox_EnblAdjust)
        flay.addRow(label_AutoAdjust, hbox_AutoAdjust)
        flay.addRow(label_PixelScale, hbox_PixelScale)
        flay.addRow(label_PixelOffset, hbox_PixelOffset)
        flay.addRow(label_EnblLowClip, hbox_EnblLowClip)
        flay.addRow(label_LowClip, hbox_LowClip)
        flay.addRow(label_EnblHighClip, hbox_EnblHighClip)
        flay.addRow(label_HighClip, hbox_HighClip)
        flay.addRow(label_EnblBG, hbox_EnblBG)
        flay.addRow(label_SaveBG, hbox_SaveBG)
        flay.addRow(label_ValidBG, hbox_ValidBG)
        return wid

    def _ROIWidget(self):
        label_MaxWidth = QLabel('Maximum Width [pixels]:', self)
        self.lb_MaxWidth = SiriusLabel(
            self, self.cam_prefix.substitute(propty='SensorWidth-Cte'))
        self.lb_MaxWidth.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_MaxHeight = QLabel('Maximum Height [pixels]:', self)
        self.lb_MaxHeight = SiriusLabel(
            self, self.cam_prefix.substitute(propty='SensorHeight-Cte'))
        self.lb_MaxHeight.setStyleSheet(
            """max-width:7.10em; max-height:1.29em;""")

        label_ROIWidth = QLabel('Width [pixels]:', self)
        hbox_ROIWidth = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIWidth', propty_type='sprb')

        label_ROIHeight = QLabel('Heigth [pixels]:', self)
        hbox_ROIHeight = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIHeight', propty_type='sprb')

        label_ROIOffsetX = QLabel('Offset X [pixels]:', self)
        hbox_ROIOffsetX = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIOffsetX', propty_type='sprb')

        label_ROIOffsetY = QLabel('Offset Y [pixels]:', self)
        hbox_ROIOffsetY = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIOffsetY', propty_type='sprb')

        label_AutoCenterX = QLabel('Auto Center X:', self)
        hbox_AutoCenterX = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIAutoCenterX', propty_type='offon')

        label_AutoCenterY = QLabel('Auto Center Y:', self)
        hbox_AutoCenterY = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AOIAutoCenterY', propty_type='offon')

        wid = QWidget()
        flay = QFormLayout(wid)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label_MaxWidth, self.lb_MaxWidth)
        flay.addRow(label_MaxHeight, self.lb_MaxHeight)
        flay.addRow(label_ROIWidth, hbox_ROIWidth)
        flay.addRow(label_ROIHeight, hbox_ROIHeight)
        flay.addRow(label_ROIOffsetX, hbox_ROIOffsetX)
        flay.addRow(label_ROIOffsetY, hbox_ROIOffsetY)
        flay.addRow(label_AutoCenterX, hbox_AutoCenterX)
        flay.addRow(label_AutoCenterY, hbox_AutoCenterY)
        return wid


class BaslerCamAcqAdvSettings(QWidget):

    def __init__(self, parent=None, device='', prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(device)
        self.cam_prefix = self.device.substitute(propty=self.prefix)
        self.setObjectName(self.device.sec + 'App')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>' + self.device +
                       ' Advanced Acquisition Settings</h3>',
                       self, alignment=Qt.AlignHCenter)
        label.setStyleSheet('max-height:1.29em;')

        label_DataType = QLabel('Data Type:', self)
        hbox_DataType = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='DataType', propty_type='enum')

        label_BwAssigned = QLabel('Band Width Assigned [bytes]:', self)
        hbox_BwAssigned = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='BwAssigned', propty_type='mon')

        label_BwReserve = QLabel('Band Width Reserved [%]:', self)
        hbox_BwReserve = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='BwReserve', propty_type='sprb')

        label_BwReserveAccum = QLabel('Band Width Reserved Accum. [%]:', self)
        hbox_BwReserveAccum = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='BwReserveAccum', propty_type='sprb')

        label_CurrentThroughput = QLabel('Current Throughput [bytes/s]:', self)
        hbox_CurrentThroughput = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='CurrentThroughput', propty_type='mon')

        label_MaxThroughput = QLabel('Maximum Throughput [bytes/s]:', self)
        hbox_MaxThroughput = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='MaxThroughput', propty_type='mon')

        label_FrameMaxJitter = QLabel('Frame Max Jitter [8 ns]:', self)
        hbox_FrameMaxJitter = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='FrameMaxJitter', propty_type='mon')

        label_PacketSize = QLabel('Packet Size [bytes]:', self)
        hbox_PacketSize = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='PacketSize', propty_type='sprb')

        label_PayloadSize = QLabel('Payload Size [bytes]:', self)
        hbox_PayloadSize = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='PayloadSize', propty_type='mon')

        label_InterPacketDelay = QLabel('Inter Packet Delay [8 ns]:', self)
        hbox_InterPacketDelay = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='InterPacketDelay', propty_type='sprb')

        label_ReadoutTime = QLabel('Readout Time [us]:', self)
        hbox_ReadoutTime = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ReadoutTime', propty_type='mon')

        label_ResultFrameRate = QLabel('Result Frame Rate:', self)
        hbox_ResultFrameRate = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ResultFrameRate', propty_type='mon')

        label_TransmDelay = QLabel('Inter Frame Delay [8 ns]:', self)
        hbox_TransmDelay = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='TransmDelay', propty_type='sprb')

        flay = QFormLayout(self)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignHCenter)
        flay.addRow(label)
        flay.addRow(label_DataType, hbox_DataType)
        flay.addRow(label_BwAssigned, hbox_BwAssigned)
        flay.addRow(label_BwReserve, hbox_BwReserve)
        flay.addRow(label_BwReserveAccum, hbox_BwReserveAccum)
        flay.addRow(label_CurrentThroughput, hbox_CurrentThroughput)
        flay.addRow(label_MaxThroughput, hbox_MaxThroughput)
        flay.addRow(label_FrameMaxJitter, hbox_FrameMaxJitter)
        flay.addRow(label_PacketSize, hbox_PacketSize)
        flay.addRow(label_PayloadSize, hbox_PayloadSize)
        flay.addRow(label_InterPacketDelay, hbox_InterPacketDelay)
        flay.addRow(label_ReadoutTime, hbox_ReadoutTime)
        flay.addRow(label_ResultFrameRate, hbox_ResultFrameRate)
        flay.addRow(label_TransmDelay, hbox_TransmDelay)
