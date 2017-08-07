import sys
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QSpacerItem, QLabel
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.led import PyDMLed
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
from siriuspy.namesys import SiriusPVName as _PVName


class ClockCntrler(QGroupBox):
    """Template for control of High and Low Level Clocks."""

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + self.prefix
        lg = QGridLayout(self)
        self.setLayout(lg)
        # Clock name
        self.setTitle(self.prefix.propty)
        # Control of event Mode
        lg.addItem(QSpacerItem(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        cb = PyDMCb(self, init_channel=pv_pref + "State-Sel")
        cb.setText('State')
        lg.addWidget(cb, 0, 0)
        lg.addWidget(PyDMLed(self, init_channel=pv_pref + "State-Sts"), 1, 0)
        # Control of Delay
        lg.addItem(QSpacerItem(40, 20, QSzPol.Expanding, QSzPol.Minimum),
                   0, 1, 1, 1)
        lg.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Freq-SP",
                                 precision=3), 0, 2)
        lb = PyDMLabel(self, init_channel=pv_pref + "Freq-RB")
        lb.setPrecFromPV(True)
        lb.setPrecision(3)
        lg.addWidget(lb, 1, 2)


def main():
    app = PyDMApplication()
    cl_ctrl = ClockCntrler(prefix='VAF-AS-Glob:TI-EVG:Clock0')
    cl_ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
