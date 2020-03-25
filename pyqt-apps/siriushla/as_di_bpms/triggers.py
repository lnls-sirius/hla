from qtpy.QtWidgets import QHBoxLayout, QGridLayout, QLabel, QFormLayout
from qtpy.QtCore import Qt
from pydm.widgets import PyDMPushButton, PyDMEnumComboBox
from siriuspy.diag.bpm import csdev as csbpms
from siriushla.widgets import SiriusLabel, SiriusSpinbox
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox


class PhysicalTriggers(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Physical Triggers</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 2)
        for i in range(8):
            grpbx = self.get_trigger_groupbox(i)
            gdl.addWidget(grpbx, (i // 2)+1, i % 2)

    def get_trigger_groupbox(self, idx):
        trig = 'TRIGGER{0:d}'.format(idx)
        name = trig + ': ' + csbpms.TrigExtern._fields[idx]
        grpbx = CustomGroupBox(name, self)
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
        pbt = PyDMPushButton(
            grpbx, label='Reset', pressValue=1,
            init_channel=self.get_pvname(trig+'RcvCntRst-SP'))
        hbl.addWidget(pbt)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvCnt-Mon'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        pbt = PyDMPushButton(
            grpbx, label='Reset', pressValue=1,
            init_channel=self.get_pvname(trig+'TrnCntRst-SP'))
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
        spbx = SiriusSpinbox(
            grpbx, init_channel=chan)
        spbx.showStepExponent = False
        spbx.limitsFromChannel = False
        low = self.bpmdb[pvn].get('low', -1e10)
        high = self.bpmdb[pvn].get('high', 1e10)
        spbx.setRange(low, high)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvLen-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        pvn = trig+'TrnLen-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusSpinbox(
            grpbx, init_channel=chan)
        spbx.showStepExponent = False
        spbx.limitsFromChannel = False
        low = self.bpmdb[pvn].get('low', -1e10)
        high = self.bpmdb[pvn].get('high', 1e10)
        spbx.setRange(low, high)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnLen-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        return grpbx


class LogicalTriggers(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm='', trig_tp=''):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm)
        self.trig_tp = trig_tp
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        name = self.bpm
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
        grpbx = CustomGroupBox(trig, self)
        fbl = QFormLayout(grpbx)

        lab = QLabel('', grpbx)
        hbl = QHBoxLayout()
        fbl.addRow(lab, hbl)
        name = 'Receiver'
        if not self.trig_tp:
            tname = csbpms.LogTrigIntern._fields[idx]
            if not tname.startswith('Unconn'):
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
        spbx = SiriusSpinbox(
            grpbx, init_channel=chan)
        spbx.showStepExponent = False
        spbx.limitsFromChannel = False
        low = self.bpmdb[pvn].get('low', -1e10)
        high = self.bpmdb[pvn].get('high', 1e10)
        spbx.setRange(low, high)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'RcvInSel-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        hbl.addSpacing(20)
        pvn = trig+'TrnOutSel-SP'
        chan = self.get_pvname(pvn)
        spbx = SiriusSpinbox(
            grpbx, init_channel=chan)
        spbx.showStepExponent = False
        spbx.limitsFromChannel = False
        low = self.bpmdb[pvn].get('low', -1e10)
        high = self.bpmdb[pvn].get('high', 1e10)
        spbx.setRange(low, high)
        hbl.addWidget(spbx)
        lab = SiriusLabel(
            grpbx, init_channel=self.get_pvname(trig+'TrnOutSel-RB'))
        lab.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab)
        return grpbx


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    import sys

    app = SiriusApplication()
    wind = SiriusDialog()
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    widm = LogicalTriggers(bpm=bpm_name, trig_tp='')
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
