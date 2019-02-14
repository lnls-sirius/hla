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
        lab = QLabel('<h2>'+self.bpm+'</h2>', self, alignment=Qt.AlignCenter)
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
        Window = create_window_from_widget(TriggeredAcquisition, 'TrigAcq')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('PostMortem')
        Window = create_window_from_widget(PostMortemAcquisition, 'PMAcq')
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
            MonitData, 'ContMonit', size=(32, 40))
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
        lab = QLabel('<h2>' + self.bpm + ' Triggered Acquisitions</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.setStretch(0, 3)
        vbl.addSpacing(10)
        self.stack = QStackedLayout()
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ', prefix=self.prefix, bpm=self.bpm)
        multi_pass.setObjectName('multi_pass')
        single_pass = SinglePassData(
            parent=self, prefix=self.prefix, bpm=self.bpm)
        single_pass.setObjectName('single_pass')

        self.stack.addWidget(multi_pass)
        self.stack.addWidget(single_pass)
        vbl.addLayout(self.stack)
        vbl.setStretch(1, 48)
        vbl.addSpacing(30)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm, data_prefix='ACQ')
        config.setObjectName('config')
        vbl.addWidget(config)
        vbl.setStretch(2, 21)
        vbl.addSpacing(10)

        self.setObjectName('TriggeredAcquisition')
        self.setStyleSheet("""
            #TriggeredAcquisition{
                min-width:52em;
                min-height:72em;}
            #multi_pass{
                min-width:50em;
                min-height:48em;}
            #single_pass{
                min-width:50em;
                min-height:48em;}
            #config{
                min-height:21em;}""")

    def toggle_multi_single(self, modeidx):
        self.stack.setCurrentIndex(modeidx)


class PostMortemAcquisition(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Post Mortem</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.setStretch(0, 3)
        vbl.addSpacing(10)
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ_PM', prefix=self.prefix, bpm=self.bpm)
        multi_pass.setObjectName('multi_pass')
        vbl.addWidget(multi_pass)
        vbl.setStretch(1, 48)
        vbl.addSpacing(30)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm,
            data_prefix='ACQ_PM')
        config.setObjectName('config')
        vbl.addWidget(config)
        vbl.setStretch(2, 21)
        vbl.addSpacing(10)

        self.setObjectName('PostMortemAcquisition')
        self.setStyleSheet("""
            #PostMortemAcquisition{
                min-width:52em;
                min-height:72em;}
            #multi_pass{
                min-height:48em;}
            #config{
                min-height:21em;}""")


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    import sys

    app = SiriusApplication()
    wind = SiriusDialog()
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    widm = BPMMain(wind, bpm=bpm_name)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
