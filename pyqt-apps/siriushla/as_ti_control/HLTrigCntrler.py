"""Control of High Level Triggers."""

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

PREFIX = 'fac' + PREFIX[8:]


class HLTriggerCntrler(QGroupBox):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix='', hl_props=set()):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.hl_props = hl_props
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + PREFIX + self.prefix
        lh = QHBoxLayout(self)
        self.setLayout(lh)
        # Trigger Name
        self.setTitle(self.prefix[:-1])
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Trigger State
        if 'state' in self.hl_props:
            lv = QVBoxLayout()
            lv.addWidget(QLabel('State', self))
            lv.addWidget(PyDMCb(self, init_channel=pv_pref + "State-Sel"))
            lv.addWidget(PyDMLed(self, init_channel=pv_pref + "State-Sts"))
            lh.addItem(lv)
            lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        if 'evg_param' in self.hl_props:
            # Control of event EVG Param
            lv = QVBoxLayout()
            lv.addWidget(QLabel('EVG Parameter', self))
            lv.addWidget(PyDMECB(self, init_channel=pv_pref + "EVGParam-Sel"))
            lv.addWidget(PyDMLabel(self, init_channel=pv_pref+"EVGParam-Sts"))
            lh.addItem(lv)
            lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        if 'pulses' in self.hl_props:
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
        if 'duration' in self.hl_props:
            # Control of Number of Duration
            lv = QVBoxLayout()
            lv.addWidget(QLabel('Duration of Train [ms]', self))
            lv.addWidget(PyDMSpinBox(self,
                                     init_channel=pv_pref + "Duration-SP",
                                     step=1e-4, limits_from_pv=True))
            lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Duration-RB",
                                   prec_from_pv=True))
            lh.addItem(lv)
            lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        if 'polarity' in self.hl_props:
            # Control of Number of Polarity
            lv = QVBoxLayout()
            lv.addWidget(QLabel('Polarity', self))
            lv.addWidget(PyDMECB(self, init_channel=pv_pref + "Polrty-Sel"))
            lv.addWidget(PyDMLabel(self, init_channel=pv_pref+"Polrty-Sts"))
            lh.addItem(lv)
            lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        if 'delay' in self.hl_props:
            # Control of Number of Duration
            lv = QVBoxLayout()
            lv.addWidget(QLabel('Delay [us]', self))
            lv.addWidget(PyDMSpinBox(self,
                                     init_channel=pv_pref + "Delay-SP",
                                     step=1e-4, limits_from_pv=True))
            lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Delay-RB",
                                   prec_from_pv=True))
            lh.addItem(lv)
            lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))


def main():
    """Run Example."""
    app = PyDMApplication()
    hl_props = {'evg_param', 'state', 'pulses', 'duration'}
    cl_ctrl = HLTriggerCntrler(prefix='SI-Glob:TI-Corrs:',
                               hl_props=hl_props)
    cl_ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
