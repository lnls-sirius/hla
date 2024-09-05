from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget, \
    QLabel, QGridLayout, QSizePolicy as QSzPlcy, QTabWidget
from siriushla.as_di_bpms.base import BaseWidget
from siriushla.as_di_bpms.settings import BPMAdvancedSettings
from siriushla.common.afc_acq_core.trig_acq_config import AcqBaseWindow


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
        self.wid_advcd = self._advancedSettingsWidget()

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.wid_graph, 1, 0, 3, 1)
        lay.addWidget(self.wid_basic, 1, 1)
        lay.addWidget(self.wid_advcd, 2, 1)
        lay.addWidget(self.wid_trig, 3, 1)
        lay.setColumnStretch(0, 4)
        lay.setColumnStretch(1, 1)
        self.setCentralWidget(wid)

    def _graphsWidget(self):
        # Antennas
        gp_ant = self._create_graph(
            'Antennas',
            {
                f'{self.device}:{self.ACQCORE}Ampl{ant}Data': f'Ant {ant}'
                for ant in ('A', 'B', 'C', 'D')
            },
            colors=('blue', 'red', 'green', 'magenta'),
        )
        # Positions
        gp_pos = self._create_graph(
            'Positions',
            {
                f'{self.device}:{self.ACQCORE}{data}Data': f'{data}'
                for data in ('PosX', 'PosY', 'PosQ', 'Sum')
            },
            colors=('blue', 'red', 'green', 'black'),
        )

        wid = QTabWidget(self)
        wid.setObjectName(self.sec+'Tab')
        wid.setStyleSheet("""
            #{}Tab::pane {{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }}""".format(self.sec))
        wid.addTab(gp_ant, 'Antennas')
        wid.addTab(gp_pos, 'Positions')
        return wid

    def _advancedSettingsWidget(self):
        tabwid = QTabWidget(self)
        tabwid.setObjectName(self.sec+'Tab')
        tabwid.setStyleSheet("""
            #{}Tab::pane {{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }}""".format(self.sec))

        # rates settings
        wid_ratesconf = QTabWidget(self)
        for rate in ['FOFB', 'TbT', 'FAcq']:
            items = BPMAdvancedSettings.get_acqrate_props(rate)
            grpbx = self._create_formlayout_groupbox('', items)
            wid_ratesconf.addTab(grpbx, rate)
        tabwid.addTab(wid_ratesconf, 'Acq.Rate Config.')

        # data triggered settings
        wid_datatrig = self._create_formlayout_groupbox(
            '', (
                ('DataTrigChan-Sel', 'Type of Rate as Trigger'),
                ('TriggerDataSel-SP', 'Channel'),
                ('TriggerDataPol-Sel', 'Slope'),
                ('TriggerDataThres-SP', 'Threshold'),
                ('TriggerDataHyst-SP', 'Hysteresis')
            ))
        tabwid.addTab(wid_datatrig, 'Auto Trig. Config.')

        return tabwid

    def _ratesConfigWidget(self):
        tabwid = QTabWidget(self)
        for rate in ['FOFB', 'TbT', 'FAcq']:
            items = BPMAdvancedSettings.get_acqrate_props(rate)
            grpbx = self._create_formlayout_groupbox('', items)
            tabwid.addTab(grpbx, rate)
        return tabwid


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
            },
            colors=('blue', 'red', 'green', 'magenta'),
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
