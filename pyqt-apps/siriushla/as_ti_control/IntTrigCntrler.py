"""Control of Timing devices Internal Triggers."""

import sys
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.led import PyDMLed
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import Events as _Events
from siriuspy.timesys.time_data import Clocks as _Clocks

PREFIX = 'fac' + PREFIX[8:]


class IntTrigCntrler(QGroupBox):
    """Template for control of Timing devices Internal Triggers."""

    def __init__(self, parent=None, prefix='', device='evr'):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.device = device
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + PREFIX + self.prefix
        lh = QHBoxLayout(self)
        self.setLayout(lh)
        # Trigger Name
        self.setTitle(self.prefix)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Trigger State
        lv = QVBoxLayout()
        lv.addWidget(QLabel('State', self))
        lv.addWidget(PyDMCb(self, init_channel=pv_pref + "State-Sel"))
        lv.addWidget(PyDMLed(self, init_channel=pv_pref + "State-Sts"))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of event EVG Param
        name = pv_pref + 'Event'
        enum_strings = _Events.LL_EVENTS
        if self.device.lower() == 'afc':
            name = pv_pref + 'EVGParam'
            enum_strings += sorted(_Clocks.LL2HL_MAP.keys())
        lv = QVBoxLayout()
        lv.addWidget(QLabel('EVG Parameter', self))
        ecb = PyDMECB(self, init_channel=name + "-Sel", type_value=str)
        ecb.set_items(enum_strings)
        ecb.setEditable(True)
        # ecb.setMaxVisibleItems(6)
        lv.addWidget(ecb)
        lv.addWidget(PyDMLabel(self, init_channel=name + "-Sts"))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Number of Pulses
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Nr Pulses', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Pulses-SP",
                                 step=1, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Pulses-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Number of Duration
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Width of Pulses [us]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Width-SP",
                                 step=1e-3, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Width-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Number of Polarity
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Polarity', self))
        lv.addWidget(PyDMECB(self, init_channel=pv_pref + "Polrty-Sel"))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref+"Polrty-Sts"))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Delay
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Delay [us]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Delay-SP",
                                 step=1e-3, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Delay-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))


def main():
    """Run Example."""
    app = PyDMApplication()
    # ctrl = IntTrigCntrler(prefix='AS-Glob:TI-EVR-1:IntTrig00', device='evr')
    ctrl = IntTrigCntrler(prefix='AS-01:TI-AFC:CRT0', device='afc')
    ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
