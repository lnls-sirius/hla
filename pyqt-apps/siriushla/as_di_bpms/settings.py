from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QPushButton
from qtpy.QtCore import Qt
from siriushla.widgets import SiriusLedState
from siriushla import util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.triggers import PhysicalTriggers, LogicalTriggers


class ParamsSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addSpacing(10)

        hbl = QHBoxLayout()
        hbl.setSpacing(15)
        hbl.addStretch()
        grpbx = CustomGroupBox('Status', self)
        gdl = QGridLayout(grpbx)
        props = (
            ('asyn.CNCT', 'Connected'),
            ('asyn.ENBL', 'Enabled'),
            ('RFFEasyn.CNCT', 'RFFE Connected'),
            ('RFFEasyn.ENBL', 'RFFE Enabled'),
            ('ADCAD9510PllStatus-Mon', 'Clock Synched'))
        for i, prop in enumerate(props):
            led = SiriusLedState(grpbx, init_channel=self.get_pvname(prop[0]))
            led.setOffColor(led.Red)
            lab = QLabel(prop[1], grpbx)
            gdl.addWidget(led, i, 0)
            gdl.addWidget(lab, i, 1)
        hbl.addWidget(grpbx)
        hbl.addStretch()

        grpbx = CustomGroupBox('Advanced Settings', self)
        vbl2 = QVBoxLayout(grpbx)
        vbl2.setSpacing(10)
        pbt = QPushButton('Software')
        Window = create_window_from_widget(
            AdvancedSettings, title=self.bpm+': Advanced Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        pbt = QPushButton('Hardware')
        Window = create_window_from_widget(
            HardwareSettings, title=self.bpm+': Hardware Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        hbl.addWidget(grpbx)
        hbl.addStretch()
        vbl.addItem(hbl)
        vbl.addSpacing(20)
        vbl.addStretch()

        grpbx = self._create_formlayout_groupbox('Offset Parameters', (
            ('PosQOffset-SP', 'Offset PosQ'),
            ('PosXOffset-SP', 'Offset PosX'),
            ('PosYOffset-SP', 'Offset PosY')))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()
        grpbx = self._create_formlayout_groupbox('Gain Parameters', (
            ('PosKq-SP', 'Gain PosQ'),
            ('PosKsum-SP', 'Gain Sum'),
            ('PosKx-SP', 'Gain PosX'),
            ('PosKy-SP', 'Gain PosY')))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()
        grpbx = self._create_formlayout_groupbox('Informations', (
            ('INFOHarmonicNumber-SP', 'Harmonic Number'),
            ('INFOFOFBRate-SP', 'FOFB Rate'),
            ('INFOMONITRate-SP', 'Monitor Rate'),
            ('INFOTBTRate-SP', 'TbT Rate'),
            ('RFFEAtt-SP', 'RFFE Attenuation')))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()


class AdvancedSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Advanced Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 2)

        grpbx = self._create_formlayout_groupbox('Monit', (
            ('MonitEnable-Sel', 'Enable'),
            ('MONITUpdtTime-SP', 'Update Time')))
        gdl.addWidget(grpbx, 1, 0)

        grpbx = self._create_formlayout_groupbox('Switching', (
            ('SwMode-Sel', 'Mode'),
            ('SwTagEn-Sel', 'Tag Enable'),
            ('SwDataMaskEn-Sel', 'Data Mask Enable'),
            ('SwDataMaskSamples-SP', 'Data Mask Samples'),
            ('SwDly-SP', 'Delay'),
            ('SwDivClk-SP', 'Division Clock')))
        gdl.addWidget(grpbx, 2, 0)

        grpbx = self._create_formlayout_groupbox('RFFE', (
            ('RFFEAtt-SP', 'Attenuation'),
            ('RFFEPidSpAC-SP', 'Pid Setpoint AC'),
            ('RFFEPidSpBD-SP', 'Pid Setpoint BD'),
            ('RFFEHeaterAC-SP', 'Heater AC'),
            ('RFFEHeaterBD-SP', 'Heater BD'),
            ('RFFEPidACKp-SP', 'Pid AC Kp'),
            ('RFFEPidBDKp-SP', 'Pid BD Kp'),
            ('RFFEPidACTi-SP', 'Pid AC Ti'),
            ('RFFEPidBDTi-SP', 'Pid BD Ti'),
            ('RFFEPidACTd-SP', 'Pid AC Td'),
            ('RFFEPidBDTd-SP', 'Pid BD Td')))
        gdl.addWidget(grpbx, 1, 1, 2, 1)

        grpbx = CustomGroupBox('Triggers Configuration', self)
        hbl = QHBoxLayout(grpbx)
        hbl.setSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('Physical Triggers')
        Window = create_window_from_widget(
            PhysicalTriggers, title=self.bpm+': Physical Triggers')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addStretch()
        pbt = QPushButton('ACQ Logical Triggers')
        Window = create_window_from_widget(
            LogicalTriggers, title=self.bpm+': ACQ Logical Triggers')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm,
            trig_tp='')
        hbl.addWidget(pbt)
        hbl.addStretch()
        pbt = QPushButton('Post-Mortem Logical Triggers')
        Window = create_window_from_widget(
            LogicalTriggers, title=self.bpm+': Post-Mortem Logical Triggers')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm,
            trig_tp='_PM')
        hbl.addWidget(pbt)
        hbl.addStretch()
        gdl.addWidget(grpbx, 3, 0, 1, 2)


class HardwareSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        hbl = QHBoxLayout(self)
        lab = QLabel('<h2>Not Implemented Yet. Open CsStudio Interfaces</h2>')
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
