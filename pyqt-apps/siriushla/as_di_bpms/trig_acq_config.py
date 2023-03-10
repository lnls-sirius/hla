from qtpy.QtWidgets import QGridLayout, QLabel, QGroupBox
from qtpy.QtCore import Qt
from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusLabel
from siriushla.as_di_bpms.base import BaseWidget


class ACQTrigConfigs(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm='', data_prefix='ACQ'):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm, data_prefix=data_prefix)
        self.setupui()

    def setupui(self):
        self.layoutg = QGridLayout(self)

        grpbx = self._create_formlayout_groupbox(
            'General Configurations', (
                ('BPMMode-Sel', 'Operation Mode'),
                ('TriggerRep-Sel', 'Repeat Acquisitions'),
                ('TriggerHwDly-SP', 'Delay [us]'),
                ('SamplesPre-SP', 'Pre-Trigger NrSamples'),
                ('SamplesPost-SP', 'Post-Trigger NrSamples'),
                ('Trigger-Sel', 'Trigger Type')))
        self.layoutg.addWidget(grpbx, 0, 0)

        grpbx = QGroupBox('Acquisition Control', self)
        gdl = QGridLayout(grpbx)
        pb1 = PyDMPushButton(
            grpbx, init_channel=self.get_pvname('TriggerEvent-Sel'),
            label='Start', pressValue=0)
        gdl.addWidget(pb1, 0, 0)
        pb2 = PyDMPushButton(
            grpbx, init_channel=self.get_pvname('TriggerEvent-Sel'),
            label='Stop', pressValue=1)
        gdl.addWidget(pb2, 0, 1)
        pb1 = PyDMPushButton(
            grpbx, init_channel=self.get_pvname('TriggerEvent-Sel'),
            label='Abort', pressValue=2)
        gdl.addWidget(pb1, 1, 0)
        lab = QLabel('Status:')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 2, 0)
        lab = SiriusLabel(grpbx, init_channel=self.get_pvname('Status-Sts'))
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 2, 1)
        lab = QLabel('Count:')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 3, 0)
        lab = SiriusLabel(grpbx, init_channel=self.get_pvname('Count-Mon'))
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 3, 1)
        self.layoutg.addWidget(grpbx, 1, 0)

        grpbx = self._create_formlayout_groupbox(
            'MultiBunch Configurations', (
                ('Channel-Sel', 'Acquisition Rate'),
                ('Shots-SP', 'Number of Shots'),
                ('UpdateTime-SP', 'Update Interval'),
                ('TbTTagEn-Sel', 'Sync Timing', False),
                ('TbTTagDly-SP', 'TbT Delay', False),
                ('TbTDataMaskEn-Sel', 'Mask Data', False),
                ('TbTDataMaskSamplesBeg-SP', 'Mask Begin', False),
                ('TbTDataMaskSamplesEnd-SP', 'Mask End', False),
                ))
        grpbx.rules = self.basic_rule('BPMMode-Sts', True)
        self.layoutg.addWidget(grpbx, 2, 0)

        grpbx = self._create_formlayout_groupbox(
            'Auto Trigger Configurations', (
                ('DataTrigChan-Sel', 'Type of Rate as Trigger'),
                ('TriggerDataSel-SP', 'Channel'),
                ('TriggerDataPol-Sel', 'Slope'),
                ('TriggerDataThres-SP', 'Threshold'),
                ('TriggerDataHyst-SP', 'Hysteresis')))
        grpbx.rules = self.basic_rule('Trigger-Sts', True, val=2)
        self.layoutg.addWidget(grpbx, 3, 0)

    def basic_rule(self, channel, flag, val=0):
        chan = self.get_pvname(channel)
        opr = '==' if flag else '!='
        val = str(val)
        rules = (
            '[{"name": "VisRule", "property": "Visible", ' +
            '"expression": "ch[0] '+opr+' '+val+'", "channels": ' +
            '[{"channel": "'+chan+'", "trigger": true}]}]')
        return rules
