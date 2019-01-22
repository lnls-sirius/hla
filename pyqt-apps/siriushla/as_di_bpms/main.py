from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, \
    QStackedLayout, QLabel
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel, SiriusConnectionSignal
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.settings import ParamsSettings
from siriushla.as_di_bpms.multiturn_data import MultiTurnData
from siriushla.as_di_bpms.singlepass_data import SinglePassData
from siriushla.as_di_bpms.trig_acq_config import ACQTrigConfigs
from siriushla.as_di_bpms.monit import MonitData


class BPMSummary(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        hbl = QHBoxLayout(self)
        hbl.addSpacing(10)
        hbl.addStretch()
        chan2vals = {
            'asyn.CNCT': 1, 'asyn.ENBL': 1,
            'RFFEasyn.CNCT': 1, 'RFFEasyn.ENBL': 1}
        chan2vals = {self.get_pvname(k): v for k, v in chan2vals.items()}
        led = PyDMLedMultiChannel(self, channels2values=chan2vals)
        hbl.addWidget(led)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton(self.bpm)
        Window = create_window_from_widget(
            BPMMain, 'BPMMain', is_main=True)
        util.connect_window(
            pbt, Window, parent=None, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()


class BPMMain(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        self.layoutv = QVBoxLayout(self)
        lab = QLabel(self.bpm, self)
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
        self.layoutv.addWidget(lab)
        self.layoutv.addSpacing(30)

        grpbx = CustomGroupBox('BPM General Status', self)
        hbl = QHBoxLayout(grpbx)
        hbl.addSpacing(10)
        hbl.addStretch()
        chan2vals = {
            'asyn.CNCT': 1, 'asyn.ENBL': 1,
            'RFFEasyn.CNCT': 1, 'RFFEasyn.ENBL': 1}
        chan2vals = {self.get_pvname(k): v for k, v in chan2vals.items()}
        led = PyDMLedMultiChannel(self, channels2values=chan2vals)
        hbl.addWidget(led)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('Open Settings')
        Window = create_window_from_widget(ParamsSettings, 'ParamsSettings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        self.layoutv.addWidget(grpbx)
        self.layoutv.addSpacing(20)
        self.layoutv.addStretch()

        grpbx = CustomGroupBox('Triggered Acquisitions', self)
        hbl = QHBoxLayout(grpbx)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('MultiBunch/SinglePass')
        Window = create_window_from_widget(
            TriggeredAcquisition, 'TrigAcq', size=(1400, 1800))
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('PostMortem')
        Window = create_window_from_widget(
            PostMortemAcquisition, 'PMAcq', size=(1400, 1800))
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        self.layoutv.addWidget(grpbx)
        self.layoutv.addSpacing(20)
        self.layoutv.addStretch()

        grpbx = self._create_formlayout_groupbox('Monitoring', (
            ('PosX-Mon', 'Position X'),
            ('PosY-Mon', 'Position Y'),
            ('PosQ-Mon', 'Position Q'),
            ('Sum-Mon', 'Sum')))
        hbl = QHBoxLayout()
        hbl.addStretch()
        pbt = QPushButton('Open Graphics', grpbx)
        hbl.addWidget(pbt)
        hbl.addStretch()
        Window = create_window_from_widget(
            MonitData, 'ContMonit', size=(1000, 1200))
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        grpbx.layoutf.addRow(hbl)
        grpbx.layoutf.setSpacing(10)
        self.layoutv.addWidget(grpbx)
        self.layoutv.addSpacing(20)
        self.layoutv.addStretch()


class TriggeredAcquisition(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()
        mode = SiriusConnectionSignal(self.get_pvname('ACQBPMMode-Sts'))
        mode.new_value_signal[int].connect(self.toggle_multi_single)
        self._chans.append(mode)

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel(self.bpm + '  Triggered Acquisitions')
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
        vbl.addWidget(lab)
        vbl.addSpacing(10)
        self.stack = QStackedLayout()
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ', prefix=self.prefix, bpm=self.bpm)
        single_pass = SinglePassData(
            parent=self, prefix=self.prefix, bpm=self.bpm)

        self.stack.addWidget(multi_pass)
        self.stack.addWidget(single_pass)
        vbl.addLayout(self.stack)
        vbl.addSpacing(30)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm, data_prefix='ACQ')
        vbl.addWidget(config)
        vbl.addSpacing(10)

    def toggle_multi_single(self, modeidx):
        self.stack.setCurrentIndex(modeidx)


class PostMortemAcquisition(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel(self.bpm + '  Post Mortem')
        lab.setAlignment(Qt.AlignCenter)
        lab.setStyleSheet("font: 30pt \"Sans Serif\";\nfont-weight: bold;")
        vbl.addWidget(lab)
        vbl.addSpacing(10)
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ_PM', prefix=self.prefix, bpm=self.bpm)
        vbl.addWidget(multi_pass)
        vbl.addSpacing(30)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm,
            data_prefix='ACQ_PM')
        vbl.addWidget(config)
        vbl.addSpacing(10)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    import sys

    app = SiriusApplication()
    wind = SiriusDialog()
    # wind.resize(1400, 1400)
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    widm = BPMMain(wind, bpm=bpm_name)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
