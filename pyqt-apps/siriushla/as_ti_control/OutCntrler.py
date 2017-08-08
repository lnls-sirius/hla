"""Control of Timing Devices Output Channels."""

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


class OutChanCntrler(QGroupBox):
    """Template for control of Timing Devices Output Channels."""

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

        # Control of event EVG Param
        num = 24 if self.device.lower() == 'evr' else 16
        enum_strings = (['IntTrig{0:02d}'.format(i) for i in range(num)] +
                        sorted(_Clocks.LL2HL_MAP.keys()))
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Internal Trigger', self))
        ecb = PyDMECB(self, init_channel=pv_pref+"IntChan-Sel", type_value=str)
        ecb.set_items(enum_strings)
        ecb.setEditable(True)
        # ecb.setMaxVisibleItems(6)
        lv.addWidget(ecb)
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "IntChan-Sts"))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Delay
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Delay [us]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Delay-SP",
                                 step=1e-4, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Delay-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        # Control of Fine Delay
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Fine Delay [ps]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "FineDelay-SP",
                                 step=1, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "FineDelay-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))


def main():
    """Run Example."""
    app = PyDMApplication()
    # ctrl = OutChanCntrler(prefix='AS-Glob:TI-EVR-1:OUT0', device='evr')
    ctrl = OutChanCntrler(prefix='AS-Glob:TI-EVE-1:OUT0', device='eve')
    ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
