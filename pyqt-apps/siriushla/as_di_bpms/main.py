from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.settings import ParamsSettings
from siriushla.as_di_bpms.monit import MonitData
from siriushla.as_di_bpms.trig_acq_config import BPMGENAcquisition, \
    BPMPMAcquisition, PBPMGENAcquisition, PBPMPMAcquisition
from siriushla.si_ap_orbintlk import BPMOrbIntlkDetailWindow


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
