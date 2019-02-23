"""SiriusScrnView widget."""

from qtpy.QtWidgets import QFormLayout, QSizePolicy as QSzPlcy, QVBoxLayout, \
                           QSpacerItem, QGroupBox, QLabel
from qtpy.QtCore import Qt
from siriuspy.namesys.implementation import SiriusPVName
from siriushla.widgets.windows import SiriusDialog
from siriushla.as_di_scrns.base import \
    create_propty_layout as _create_propty_layout


class ScrnCalibrationSettings(SiriusDialog):
    """Scrn Calibration Settings Dialog."""

    def __init__(self, parent=None, device=None, prefix=None):
        """Init."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.device = device
        self.scrn_prefix = self.prefix+self.device
        self.setWindowTitle('Screen Calibration')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>'+self.scrn_prefix+' Calibration</h3>', self,
                       alignment=Qt.AlignCenter)

        positioning = QGroupBox('Positioning', self)

        label_AcceptedErr = QLabel('Error Tolerance [mm]: ', self)
        hbox_AcceptedErr = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='AcceptedErr',
            propty_type='sprb')

        label_FluorScrnPos = QLabel('Fluorescent Screen Position [mm]: ', self)
        hbox_FluorScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='FluorScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetFluorScrnPos'})

        label_CalScrnPos = QLabel('Calibration Screen Position [mm]: ', self)
        hbox_CalScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='CalScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetCalScrnPos'})

        label_NoneScrnPos = QLabel('Receded Screen Position [mm]: ', self)
        hbox_NoneScrnPos = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='NoneScrnPos',
            propty_type='sprb', cmd={'label': 'Get Position',
                                     'pressValue': 1,
                                     'name': 'GetNoneScrnPos'})

        LED = QGroupBox('LED Brightness', self)

        label_LedPwrLvl = QLabel('Intensity [%]: ', self)
        hbox_LedPwrLvl = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDPwrLvl',
            propty_type='sprb')

        label_LedPwrScaleFactor = QLabel('Power Scale Factor: ', self)
        hbox_LedPwrScaleFactor = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDPwrScaleFactor',
            propty_type='sprb')

        label_LedThold = QLabel('Voltage Threshold [V]: ', self)
        hbox_LedThold = _create_propty_layout(
            parent=self, prefix=self.scrn_prefix, propty='LEDThold',
            propty_type='sprb')

        Img = QGroupBox('Statistics Unit Conversion (Pixels→mm)', self)

        cam_prefix = SiriusPVName(self.scrn_prefix).substitute(dev='ScrnCam')

        label_ImgScaleFactor = QLabel('Scale Factor: ', self)
        hbox_ImgScaleFactor = _create_propty_layout(
            parent=self, prefix=cam_prefix, propty='ImgScaleFactor',
            propty_type='sprb')

        label_ImgCenterOffsetX = QLabel('Center Offset X: ', self)
        hbox_ImgCenterOffsetX = _create_propty_layout(
            parent=self, prefix=cam_prefix, propty='ImgCenterOffsetX',
            propty_type='sprb')

        label_ImgCenterOffsetY = QLabel('Center Offset Y: ', self)
        hbox_ImgCenterOffsetY = _create_propty_layout(
            parent=self, prefix=cam_prefix, propty='ImgCenterOffsetY',
            propty_type='sprb')

        positioning.setStyleSheet("""
            .QLabel{
                min-width:16em;\nmax-width:16em;
                qproperty-alignment: AlignRight;\n}""")
        LED.setStyleSheet("""
            .QLabel{
                min-width:11em;\nmax-width:11em;
                qproperty-alignment: AlignRight;\n}""")
        Img.setStyleSheet("""
            .QLabel{
                min-width:8em;\nmax-width:8em;
                qproperty-alignment: AlignRight;\n}""")

        flay_pos = QFormLayout()
        flay_pos.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_pos.addRow(label_AcceptedErr, hbox_AcceptedErr)
        flay_pos.addRow(label_FluorScrnPos, hbox_FluorScrnPos)
        flay_pos.addRow(label_CalScrnPos, hbox_CalScrnPos)
        flay_pos.addRow(label_NoneScrnPos, hbox_NoneScrnPos)
        flay_pos.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_pos.setLabelAlignment(Qt.AlignRight)
        flay_pos.setFormAlignment(Qt.AlignCenter)
        positioning.setLayout(flay_pos)

        flay_LED = QFormLayout()
        flay_LED.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_LED.addRow(label_LedPwrLvl, hbox_LedPwrLvl)
        flay_LED.addRow(label_LedPwrScaleFactor, hbox_LedPwrScaleFactor)
        flay_LED.addRow(label_LedThold, hbox_LedThold)
        flay_LED.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_LED.setLabelAlignment(Qt.AlignRight)
        flay_LED.setFormAlignment(Qt.AlignCenter)
        LED.setLayout(flay_LED)

        flay_Img = QFormLayout()
        flay_Img.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_Img.addRow(label_ImgScaleFactor, hbox_ImgScaleFactor)
        flay_Img.addRow(label_ImgCenterOffsetX, hbox_ImgCenterOffsetX)
        flay_Img.addRow(label_ImgCenterOffsetY, hbox_ImgCenterOffsetY)
        flay_Img.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        flay_Img.setLabelAlignment(Qt.AlignRight)
        flay_Img.setFormAlignment(Qt.AlignCenter)
        Img.setLayout(flay_Img)

        vlay = QVBoxLayout()
        vlay.addWidget(label)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(positioning)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(LED)
        vlay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))
        vlay.addWidget(Img)
        self.setLayout(vlay)
