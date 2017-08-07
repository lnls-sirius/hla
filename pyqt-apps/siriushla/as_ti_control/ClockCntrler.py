import sys
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.led import PyDMLed
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

PREFIX = 'fac' + PREFIX[8:]


class ClockCntrler(QGroupBox):
    """Template for control of High and Low Level Clocks."""

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + PREFIX + self.prefix
        lh = QHBoxLayout(self)
        self.setLayout(lh)
        # Clock name
        self.setTitle(self.prefix.propty)

        # Clock State
        lv = QVBoxLayout()
        lv.addWidget(QLabel('State', self))
        lv.addWidget(PyDMCb(self, init_channel=pv_pref + "State-Sel"))
        lv.addWidget(PyDMLed(self, init_channel=pv_pref + "State-Sts"))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))

        # Control of Delay
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Frequency [kHz]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Freq-SP",
                                 step=1e-4, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Freq-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))


def main():
    """Run Example."""
    app = PyDMApplication()
    cl_ctrl = ClockCntrler(prefix='AS-Glob:TI-EVG:Clock0')
    cl_ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
