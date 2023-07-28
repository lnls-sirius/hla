"""Trigger windows."""

from qtpy.QtWidgets import QHBoxLayout, QGridLayout, QLabel, QFormLayout, \
    QGroupBox
from qtpy.QtCore import Qt

from pydm.widgets import PyDMPushButton, PyDMEnumComboBox

from siriuspy.namesys import SiriusPVName
from siriuspy.search import HLTimeSearch

from ...widgets import SiriusLabel, SiriusLineEdit

from .base import BaseWidget


class PhysicalTriggers(BaseWidget):
    """Physical triggers."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(parent=parent, prefix=prefix, device=device)
        self.afctiming = SiriusPVName(
            f'IA-{self.device.sub[:2]}RaBPM:TI-AMCFPGAEVR')
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.device + ' Physical Triggers</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 2)
        for i in range(8):
            grpbx = self.get_trigger_groupbox(i)
            gdl.addWidget(grpbx, (i // 2)+1, i % 2)

    def get_trigger_groupbox(self, idx):
        trig = 'TRIGGER{0:d}'.format(idx)
        hltrig = 'Monit' if idx == 7 else HLTimeSearch.get_hl_from_ll_triggers(
            self.afctiming.substitute(propty_name=f'CRT{idx}'))
        name = trig + (': ' + hltrig if hltrig else '')
        grpbx = QGroupBox(name, self)
        fbl = QFormLayout(grpbx)

        hbl = QHBoxLayout()
        lab = QLabel('Direction', grpbx)
        fbl.addRow(lab, hbl)
        enum = PyDMEnumComboBox(
            grpbx, init_channel=self.get_pvname(trig+'Dir-Sel'))
        hbl.addWidget(enum)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'Dir-Sts'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        hbl = QHBoxLayout()
        lab = QLabel('Polarity', grpbx)
        fbl.addRow(lab, hbl)
        enum = PyDMEnumComboBox(
            grpbx, init_channel=self.get_pvname(trig+'DirPol-Sel'))
        hbl.addWidget(enum)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'DirPol-Sts'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        lab = QLabel('', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        lab = QLabel('Receiver', grpbx)
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(15)
        lab = QLabel('Transmitter', grpbx)
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        lab = QLabel('Counter', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        suf = 'SP' if 'BPM' in self.device else 'Cmd'
        pbt = PyDMPushButton(
            grpbx, label='Reset', pressValue=1,
            init_channel=self.get_pvname(trig+'RcvCntRst-'+suf))
        hbl.addWidget(pbt)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvCnt-Mon'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        suf = 'SP' if 'BPM' in self.device else 'Cmd'
        pbt = PyDMPushButton(
            grpbx, label='Reset', pressValue=1,
            init_channel=self.get_pvname(trig+'TrnCntRst-'+suf))
        hbl.addWidget(pbt)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnCnt-Mon'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        lab = QLabel('Length', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        pvn = trig+'RcvLen-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusLineEdit(grpbx, init_channel=chan)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvLen-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        pvn = trig+'TrnLen-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusLineEdit(grpbx, init_channel=chan)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnLen-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        return grpbx


class LogicalTriggers(BaseWidget):
    """Logical triggers."""

    def __init__(
            self, parent=None, prefix='', device='', names=None, trig_tp=''):
        super().__init__(parent=parent, prefix=prefix, device=device)
        self.trig_tp = trig_tp
        self.names = names
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        name = self.device
        if self.trig_tp:
            name += ' ' + self.trig_tp[1:]
        lab = QLabel('<h2>' + name + ' Logical Triggers</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 3)
        for i in range(24):
            grpbx = self.get_trigger_groupbox(i)
            gdl.addWidget(grpbx, (i // 3)+1, i % 3)

    def get_trigger_groupbox(self, idx):
        trig = 'TRIGGER{0:s}{1:d}'.format(self.trig_tp, idx)
        grpbx = QGroupBox(trig, self)
        fbl = QFormLayout(grpbx)

        lab = QLabel('', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        name = 'Receiver'
        if not self.trig_tp:
            tname = self.names[idx] if self.names else ''
            if tname and not tname.startswith('Unconn'):
                name += ': ' + tname
        lab = QLabel(name, grpbx)
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(15)
        lab = QLabel('Transmitter', grpbx)
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        lab = QLabel('Source', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        enum = PyDMEnumComboBox(
            grpbx, init_channel=self.get_pvname(trig+'RcvSrc-Sel'))
        hbl.addWidget(enum)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvSrc-Sts'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        enum = PyDMEnumComboBox(
            grpbx, init_channel=self.get_pvname(trig+'TrnSrc-Sel'))
        hbl.addWidget(enum)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnSrc-Sts'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)

        lab = QLabel('Selection', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        pvn = trig+'RcvInSel-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusLineEdit(grpbx, init_channel=chan)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvInSel-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        pvn = trig+'TrnOutSel-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusLineEdit(grpbx, init_channel=chan)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnOutSel-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        return grpbx
