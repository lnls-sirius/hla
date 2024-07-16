from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget, \
    QLabel, QGridLayout, QSizePolicy as QSzPlcy, QTabWidget
from siriushla.as_di_bpms.base import BaseWidget
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
