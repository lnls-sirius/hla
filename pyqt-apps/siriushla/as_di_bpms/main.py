from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from siriushla import util
from siriushla.widgets import PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.as_di_bpms.settings import ParamsSettings, AFCAdvancedSettings
from siriushla.as_di_bpms.monit import MonitData
from siriushla.as_di_bpms.trig_acq_config import BPMGENAcquisition, \
    BPMPMAcquisition, PBPMGENAcquisition, PBPMPMAcquisition
from siriushla.si_ap_orbintlk import BPMOrbIntlkDetailWindow
from siriushla.as_di_bpms import afcs_pvs
import qtawesome as qta
from siriushla.widgets import SiriusPushButton, SiriusLabel


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
            chan2vals = {'RFFEasyn.CNCT': 1, 'ClksLocked-Mon': 1}
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
        if self.bpm[:2] == 'SI':
            if self.bpm[5:9] == 'SBFE' or self.bpm[5:9] == 'SPFE' or self.bpm[5:9] == 'SAFE':
                self._amcFRU(4)

            elif self.bpm[5:9] == 'BCFE':
                self._amcFRU(5)

            elif self.bpm[5:8] == 'SA:' or self.bpm[5:8] == 'SB:' or self.bpm[5:8] == 'SP:':
                self._amcFRU(6)

            elif self.bpm[5:7] == 'M1' or self.bpm[5:7] == 'M2':
                self._amcFRU(7)

            elif self.bpm[5:7] == 'C1':
                self._amcFRU(8)

            elif self.bpm[5:7] == 'C2' or self.bpm[5:16] == 'C3:DI-BPM-1':
                self._amcFRU(9)

            elif self.bpm[5:7] == 'C4' or self.bpm[5:16] == 'C3:DI-BPM-2':
                self._amcFRU(10)

        elif self.bpm[:2] == 'BO':
            if int(self.bpm[3:5]) in afcs_pvs.BO_N or int(self.bpm[3:5]) - 1 in afcs_pvs.BO_N:
                self._amcFRU(11)

            elif int(self.bpm[3:5]) - 2 in afcs_pvs.BO_N:
                self._amcFRU(12)

        elif self.bpm[:2] == 'TB':
            if self.bpm[3:5] == '01':
                self._amcFRU(6)

            elif self.bpm[3:5] == '02':
                self._amcFRU(7)

            elif self.bpm[3:5] == '03' or self.bpm[3:5] == '04':
                self._amcFRU(8)

        elif self.bpm[:2] == 'TS':
            if self.bpm[3:5] == '01' or self.bpm[3:5] == '02':
                self._amcFRU(9)

            elif self.bpm[3:5] == '03' or self.bpm[3:14] == '04:DI-BPM-1':
                self._amcFRU(10)

            elif self.bpm[3:14] == '04:DI-BPM-2':
                self._amcFRU(11)

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

    def _amcFRU(self, i):
        pbt = QPushButton('AFC Settings')
        Window = create_window_from_widget(
            AFCAdvancedSettings, title=self.bpm+': AFC Settings')
        util.connect_window(
            pbt, Window, parent=self, prefix=self.prefix, bpm=self.bpm)

        pv_list_fru = afcs_pvs.AFCv3_1_PV_LIST['FRU']
        grbx = CustomGroupBox('AFC Details', self)
        grbx_lay = QHBoxLayout(grbx)
        grbx_lay.setSpacing(20)

        grbx_lay.addWidget(pbt)

        if self.bpm[:2] == 'TS' or self.bpm[:2] == 'TB':
            cmd_button = SiriusPushButton(
                self, label='Reset', icon=qta.icon('mdi.restart'),
                init_channel=f"IA-20RaBPMTL:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRst']}"
                )
        elif self.bpm[:2] == 'BO':
            bo_num = int(self.bpm.split('-')[1][:2])
            if bo_num in afcs_pvs.BO_N:
                area_index = afcs_pvs.BO_N.index(bo_num) + 1
                area_str = f"{area_index:02}"
                cmd_button = SiriusPushButton(
                    self, label='Reset', icon=qta.icon('mdi.restart'),
                    init_channel=f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRst']}"
                    )
            elif bo_num in afcs_pvs.BO_N1:
                area_index = afcs_pvs.BO_N1.index(bo_num) + 1
                area_str = f"{area_index:02}"
                cmd_button = SiriusPushButton(
                    self, label='Reset', icon=qta.icon('mdi.restart'),
                    init_channel=f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRst']}"
                    )
            elif bo_num in afcs_pvs.BO_N2:
                area_index = afcs_pvs.BO_N2.index(bo_num) + 1
                area_str = f"{area_index:02}"
                cmd_button = SiriusPushButton(
                    self, label='Reset', icon=qta.icon('mdi.restart'),
                    init_channel=f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRst']}"
                    )
        else:
            cmd_button = SiriusPushButton(
                self, label='Reset', icon=qta.icon('mdi.restart'),
                init_channel=f"IA-{self.bpm[3:5]}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRst']}"
                )
        grbx_lay.addWidget(cmd_button)

        if self.bpm[:2] == 'TS' or self.bpm[:2] == 'TB':
            label_mon = SiriusLabel(
                self, f"IA-20RaBPMTL:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRstSts']}"
                )
        elif self.bpm[:2] == 'BO':
            bo_num = int(self.bpm.split('-')[1][:2])
            if bo_num in afcs_pvs.BO_N:
                area_index = afcs_pvs.BO_N.index(bo_num) + 1
                area_str = f"{area_index:02}"
                label_mon = SiriusLabel(
                    self, f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRstSts']}"
                    )
            elif bo_num in afcs_pvs.BO_N1:
                area_index = afcs_pvs.BO_N1.index(bo_num) + 1
                area_str = f"{area_index:02}"
                label_mon = SiriusLabel(
                    self, f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRstSts']}"
                    )
            elif bo_num in afcs_pvs.BO_N2:
                area_index = afcs_pvs.BO_N2.index(bo_num) + 1
                area_str = f"{area_index:02}"
                label_mon = SiriusLabel(
                    self, f"IA-{area_str}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRstSts']}"
                )
        else:
            label_mon = SiriusLabel(
                self, f"IA-{self.bpm[3:5]}RaBPM:{afcs_pvs.DIS}-AMC-{i}:{pv_list_fru['SoftRstSts']}"
                )
        grbx_lay.addWidget(label_mon)
        self.layoutv.addWidget(grbx)
        self.layoutv.addSpacing(20)
