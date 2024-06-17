from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, \
    QStackedLayout, QLabel, QGridLayout, QSizePolicy as QSzPlcy, \
    QWidget
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel, SiriusConnectionSignal
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.settings import ParamsSettings
from siriushla.as_di_bpms.multiturn_data import MultiTurnData
from siriushla.as_di_bpms.singlepass_data import SinglePassData
from siriushla.as_di_bpms.trig_acq_config import ACQTrigConfigs
from siriushla.as_di_bpms.monit import MonitData
from siriushla.si_ap_orbintlk import BPMOrbIntlkDetailWindow
from siriushla.common.afc_acq_core.trig_acq_config import AcqBaseWindow


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
        if not self.is_pbpm:
            chan2vals = {'RFFEasyn.CNCT': 1, 'ADCAD9510PllStatus-Mon': 1}
            chan2vals = {self.get_pvname(k): v for k, v in chan2vals.items()}
            led = PyDMLedMultiChannel(self, channels2values=chan2vals)
            hbl.addWidget(led)
            hbl.addSpacing(10)
            hbl.addStretch()
        pbt = QPushButton('Open Settings')
        Window = create_window_from_widget(
            ParamsSettings, title=self.bpm+': Settings')
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
        acqtitle = 'MultiBunch' + ('' if self.is_pbpm else '/SinglePass')
        pbt = QPushButton(acqtitle)
        if self.is_pbpm:
            Window = PBPMGENAcquisition
        else:
            Window = create_window_from_widget(
                TriggeredAcquisition,
                title=f'{self.bpm}: {acqtitle} Acquisitions')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('PostMortem')
        if self.is_pbpm:
            Window = PBPMPMAcquisition
        else:
            Window = create_window_from_widget(
                PostMortemAcquisition,
                title=self.bpm+': PostMortem Acquisitions')
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
            MonitData, title=self.bpm+': Monit Data')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        grpbx.layoutf.addRow(hbl)
        grpbx.layoutf.setSpacing(10)
        self.layoutv.addWidget(grpbx)
        self.layoutv.addSpacing(20)
        self.layoutv.addStretch()

        if self.bpm.sec not in ['TB', 'BO', 'TS'] and not self.is_pbpm:
            grpbx = CustomGroupBox('Orbit Interlock', self)
            hbl = QHBoxLayout(grpbx)
            pbt = QPushButton('Open Interlock Settings', grpbx)
            util.connect_window(
                pbt, BPMOrbIntlkDetailWindow, parent=grpbx,
                prefix=self.prefix, device=self.bpm)
            hbl.addStretch()
            hbl.addWidget(pbt)
            hbl.addStretch()
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
        vbl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Triggered Acquisitions</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab, 0, 0, 1, 2)
        self.stack = QStackedLayout()
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ', prefix=self.prefix, bpm=self.bpm)
        multi_pass.setObjectName('multi_pass')
        single_pass = SinglePassData(
            parent=self, prefix=self.prefix, bpm=self.bpm)
        single_pass.setObjectName('single_pass')

        self.stack.addWidget(multi_pass)
        self.stack.addWidget(single_pass)
        vbl.addLayout(self.stack, 1, 0)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm, data_prefix='ACQ')
        config.setObjectName('config')
        vbl.addWidget(config, 1, 1)

        self.setStyleSheet("""
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
        vbl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Post Mortem</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab, 0, 0, 1, 2)
        multi_pass = MultiTurnData(
            parent=self, acq_type='ACQ_PM', prefix=self.prefix, bpm=self.bpm)
        multi_pass.setObjectName('multi_pass')
        vbl.addWidget(multi_pass, 1, 0)
        config = ACQTrigConfigs(
            parent=self, prefix=self.prefix, bpm=self.bpm,
            data_prefix='ACQ_PM')
        config.setObjectName('config')
        vbl.addWidget(config, 1, 1)

        self.setStyleSheet("""
            #multi_pass{
                min-height:48em;}
            #config{
                min-height:21em;}""")


class PBPMBaseTriggeredAcquisition(AcqBaseWindow):
    """Photon BPM Base Triggered Acquisition window."""

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, device=bpm)
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h2>'+self.device.substitute(propty_name=self.ACQCORE) +
            ' Acquisitions < /h2 >', alignment=Qt.AlignCenter)
        self.title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        self.wid_basic = self._basicSettingsWidget()
        self.wid_trig = self._triggersWidget()
        self.wid_graph = self._graphsWidget()

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.wid_graph, 1, 0, 2, 1)
        lay.addWidget(self.wid_basic, 1, 1)
        lay.addWidget(self.wid_trig, 2, 1)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 1)
        lay.setRowStretch(0, 3)
        lay.setRowStretch(1, 1)
        self.setCentralWidget(wid)

    def _graphsWidget(self):
        # Antennas
        gp_ant = self._create_graph(
            'Antennas',
            {
                f'{self.device}:{self.ACQCORE}Ampl{ant}Data': f'Ant {ant}'
                for ant in ('A', 'B', 'C', 'D')
            }
        )

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.addWidget(gp_ant)
        return wid


class PBPMGENAcquisition(PBPMBaseTriggeredAcquisition):
    """PBPM General Triggered Acquisition window"""

    ACQCORE = 'GEN'


class PBPMPMAcquisition(PBPMBaseTriggeredAcquisition):
    """PBPM Post Mortem Triggered Acquisition window"""

    ACQCORE = 'PM'
