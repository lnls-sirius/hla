from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, \
    QLabel, QGridLayout, QSizePolicy as QSzPlcy, QTabWidget, \
    QWidget
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.settings import ParamsSettings
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
        pbt = QPushButton('General')
        Window = PBPMGENAcquisition if self.is_pbpm else BPMGENAcquisition
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        hbl.addWidget(pbt)
        hbl.addSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('PostMortem')
        Window = PBPMPMAcquisition if self.is_pbpm else BPMPMAcquisition
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

        if self.bpm.sec not in ['TB', 'BO', 'TS']:
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


class BPMBaseTriggeredAcquisition(AcqBaseWindow, BaseWidget):
    """BPM Base Triggered Acquisition window."""

    def __init__(self, parent=None, prefix='', bpm=''):
        AcqBaseWindow.__init__(self, parent=parent, prefix=prefix, device=bpm)
        BaseWidget.__init__(
            self, parent=parent, prefix=prefix, bpm=bpm,
            data_prefix=self.ACQCORE,
        )
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h2>'+self.device.substitute(propty_name=self.ACQCORE) +
            ' Acquisitions </h2>', alignment=Qt.AlignCenter)
        self.title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        self.wid_basic = self._basicSettingsWidget()
        self.wid_trig = self._triggersWidget()
        self.wid_graph = self._graphsWidget()
        self.wid_tbtconf = self._tbtConfigWidget()
        self.wid_datatrig = self._dataTrigWidget()

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.wid_graph, 1, 0, 2, 1)
        lay.addWidget(self.wid_basic, 1, 1)
        lay.addWidget(self.wid_tbtconf, 2, 1)
        lay.addWidget(self.wid_datatrig, 3, 1)
        lay.addWidget(self.wid_trig, 4, 1)
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
        # Positions
        gp_pos = self._create_graph(
            'Positions',
            {
                f'{self.device}:{self.ACQCORE}{data}Data': f'{data}'
                for data in ('PosX', 'PosY', 'PosQ', 'Sum')
            }
        )

        wid = QTabWidget(self)
        wid.setObjectName(self.sec+'Tab')
        wid.addTab(gp_ant, 'Antennas')
        wid.addTab(gp_pos, 'Positions')
        return wid

    def _tbtConfigWidget(self):
        grpbx = self._create_formlayout_groupbox(
            'TbT Configurations', (
                ('TbTPhaseSyncEn-Sel', 'Sync Timing', False),
                ('TbTPhaseSyncDly-SP', 'TbT Delay [adc counts]',
                 dict(isdata=False, widgets=['lineedit', 'label'])),
                ('TbTDataMaskEn-Sel', 'Mask Data', False),
                ('TbTDataMaskSamplesBeg-SP', 'Mask Begin',
                 dict(isdata=False, widgets=['lineedit', 'label'])),
                ('TbTDataMaskSamplesEnd-SP', 'Mask End',
                 dict(isdata=False, widgets=['lineedit', 'label'])),
                ))
        return grpbx

    def _dataTrigWidget(self):
        grpbx = self._create_formlayout_groupbox(
            'Auto Trigger Configurations', (
                ('DataTrigChan-Sel', 'Type of Rate as Trigger'),
                ('TriggerDataSel-SP', 'Channel'),
                ('TriggerDataPol-Sel', 'Slope'),
                ('TriggerDataThres-SP', 'Threshold'),
                ('TriggerDataHyst-SP', 'Hysteresis')))
        grpbx.rules = self.basic_rule('Trigger-Sts', True, val=2)
        return grpbx


class BPMGENAcquisition(BPMBaseTriggeredAcquisition):
    """BPM General Triggered Acquisition window"""

    ACQCORE = 'GEN'


class BPMPMAcquisition(BPMBaseTriggeredAcquisition):
    """BPM Post Mortem Triggered Acquisition window"""

    ACQCORE = 'PM'


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
