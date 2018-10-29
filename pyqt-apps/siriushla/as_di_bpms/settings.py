from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QAction, QCheckBox, \
    QGridLayout, QLabel, QPushButton, QFormLayout
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
        lab = QLabel(self.bpm + ' Settings')
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
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
            ('RFFEasyn.ENBL', 'RFFE Enabled'))
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
        Window = create_window_from_widget(AdvancedSettings, 'AdvancedInfo')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        pbt = QPushButton('Hardware')
        Window = create_window_from_widget(HardwareSettings, 'HdwrSettings')
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
        lab = QLabel(self.bpm + ' Advanced Settings')
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
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
        Window = create_window_from_widget(PhysicalTriggers, 'PhysTrigs')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addStretch()
        pbt = QPushButton('ACQ Logical Triggers')
        Window = create_window_from_widget(LogicalTriggers, 'ACQTrigs')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm,
            trig_tp='')
        hbl.addWidget(pbt)
        hbl.addStretch()
        pbt = QPushButton('Post-Mortem Logical Triggers')
        Window = create_window_from_widget(LogicalTriggers, 'PMTrigs')
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
        lab = QLabel('Not Implemented Yet. Open CsStudio Interfaces')
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
        hbl.addWidget(lab)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriushla.util import set_style
    import sys

    app = SiriusApplication()
    set_style(app)
    wind = SiriusDialog()
    # wind.resize(1400, 1400)
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    widm = ParamsSettings(bpm=bpm_name)
    # widm = AdvancedSettings(bpm=bpm_name)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
