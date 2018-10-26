import sys
from epics import PV as _PV
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from PyQt5.QtWidgets import QPushButton
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinbox
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import SiriusDialog
from siriushla import util as _util
from siriushla.as_ti_control.base_list import BaseList


class HLTriggerDetailed(SiriusDialog):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)
        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 1, 0)
        self._setup_status_wid()
        self.ll_list_wid = QGroupBox('Configs', self)
        self.my_layout.addWidget(self.ll_list_wid, 1, 1)
        self._setup_ll_list_wid()

    def _setup_status_wid(self):
        status_layout = QFormLayout(self.status_wid)
        status_layout.setHorizontalSpacing(20)
        status_layout.setVerticalSpacing(20)
        pv = _PV(self.prefix[5:] + 'Status-Cte')
        labels = pv.get()
        if labels is None:
            lab = QLabel('Failed to get Status labels', self)
            status_layout.addRow(lab)
            status_layout.setAlignment(lab, Qt.AlignVCenter)
        else:
            channel = self.prefix + 'Status-Mon'
            for bit, label in enumerate(labels):
                led = SiriusLedAlert(self, channel, bit)
                lab = QLabel(label, self)
                status_layout.addRow(led, lab)

    def _setup_ll_list_wid(self):
        prefix = self.prefix
        ll_list_layout = QGridLayout(self.ll_list_wid)
        ll_list_layout.setHorizontalSpacing(20)
        ll_list_layout.setVerticalSpacing(20)

        but = QPushButton('Open LL Triggers', self)
        # _util.connect_window(
        #     but, _LLTriggerList, self,
        #     **{'prefix': self.prefix, 'interlock': 0})
        ll_list_layout.addWidget(but, 0, 0, 1, 2)

        sp = PyDMStateButton(self, init_channel=prefix + "State-Sel")
        rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        gb = self._create_small_GB('Enabled', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 0)

        sp = PyDMStateButton(self, init_channel=prefix + "Intlk-Sel")
        sp.shape = 1
        sp.setMinimumWidth(40)
        sp.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        rb = PyDMLed(self, init_channel=prefix + "Intlk-Sts")
        rb.shape = 1
        rb.setMinimumWidth(40)
        rb.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        gb = self._create_small_GB('Interlock', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 1)

        sp = PyDMECB(self, init_channel=prefix + "Src-Sel")
        rb = PyDMLabel(self, init_channel=prefix+"Src-Sts")
        gb = self._create_small_GB('Source', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 0)

        sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
        gb = self._create_small_GB('Pulses', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 1)

        sp = PyDMSpinbox(self, init_channel=prefix + "Duration-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "Duration-RB")
        gb = self._create_small_GB('Duration [ms]', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 3, 0, 1, 2)

        sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        gb = self._create_small_GB('Delay [us]', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 4, 0, 1, 2)

        sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
        rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
        gb = self._create_small_GB('Polarity', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 5, 0)

        sp = PyDMECB(self, init_channel=prefix+"DelayType-Sel")
        rb = PyDMLabel(self, init_channel=prefix+"DelayType-Sts")
        gb = self._create_small_GB('Delay Type', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 5, 1)

    def _create_small_GB(self, name, parent, wids):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
        return gb


class HLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'detailed': 280,
        'status': 150,
        'state': 120,
        'interlock': 200,
        'source': 150,
        'pulses': 100,
        'duration': 190,
        'polarity': 150,
        'delay_type': 130,
        'delay': 170,
        }
    _LABELS = {
        'detailed': 'Detailed View',
        'status': 'Status',
        'state': 'Enabled',
        'interlock': 'Interlock',
        'source': 'Source',
        'pulses': 'Pulses',
        'duration': 'Duration [ms]',
        'polarity': 'Polarity',
        'delay_type': 'Type',
        'delay': 'Delay [us]',
        }
    _ALL_PROPS = (
        'detailed', 'state', 'interlock', 'source', 'polarity', 'pulses',
        'duration', 'delay_type', 'delay', 'status',
        )

    def _createObjs(self, prefix, prop):
        if 'detailed' == prop:
            but = (QPushButton(prefix.device_name, self), )
            _util.connect_window(
                but[0], HLTriggerDetailed, self, prefix=prefix)
        elif 'status' == prop:
            rb = SiriusLedAlert(self, init_channel=prefix + "Status-Mon")
            rb.setShape(rb.ShapeMap.Square)
            but = (rb, )
        elif 'state' == prop:
            sp = PyDMStateButton(self, init_channel=prefix + "State-Sel")
            # rb = PyDMLed(self, init_channel=prefix + "State-Sts")
            but = (sp, )
        elif 'interlock' == prop:
            but = (PyDMCb(self, init_channel=prefix + "Intlk-Sel"),
                   PyDMLed(self, init_channel=prefix + "Intlk-Sts"))
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Src-Sel")
            # rb = PyDMLabel(self, init_channel=prefix+"Src-Sts")
            but = (sp, )
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
            sp.showStepExponent = False
            # rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
            but = (sp, )
        elif 'duration' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Duration-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Duration-RB")
            but = (sp, rb)
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            # rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
            but = (sp, )
        elif 'delay_type' == prop:
            but = (PyDMECB(self, init_channel=prefix+"DelayType-Sel"),
                   PyDMLabel(self, init_channel=prefix+"DelayType-Sts"))
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
            but = (sp, rb)
        else:
            raise Exception('Property unknown')
        return but


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    detail_ctrl = HLTriggerDetailed(
        prefix='ca://fernando-lnls452-linux-SI-01SA:TI-PingH:')
    detail_ctrl.show()
    props = {'detailed', 'state', 'pulses', 'duration'}
    list_ctrl = HLTriggerList(
        name="Triggers",
        prefix='ca://fernando-lnls452-linux-',
        props=props,
        obj_names=['SI-01SA:TI-PingH:', 'SI-01SA:TI-PingV:'],
        )
    list_ctrl.show()
    sys.exit(app.exec_())
