import sys
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSpacerItem, QLabel
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
from siriuspy.namesys import SiriusPVName as _PVName


class EventCntrler(QGroupBox):
    """Template for control of High and Low Level Events."""

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + self.prefix
        lh = QHBoxLayout(self)
        self.setLayout(lh)
        # Event Name
        lh.addWidget(QLabel(self.prefix.propty, self))
        # Control of event Mode
        lh.addItem(QSpacerItem(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        lh.addWidget(PyDMECB(self, init_channel=pv_pref + "Mode-Sel"))
        lh.addWidget(PyDMLabel(self, init_channel=pv_pref + "Mode-Sts"))
        # Control of DelayType
        lh.addItem(QSpacerItem(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        lh.addWidget(PyDMECB(self, init_channel=pv_pref + "DelayType-Sel"))
        lh.addWidget(PyDMLabel(self, init_channel=pv_pref + "DelayType-Sts"))
        # Control of Delay
        lh.addItem(QSpacerItem(40, 20, QSzPol.Expanding, QSzPol.Minimum))
        lh.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Delay-SP",
                                 precision=3))
        lb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB",)
        lb.setPrecFromPV(True)
        lb.setPrecision(3)
        lh.addWidget(lb)


def main():
    app = PyDMApplication()
    ev_ctrl = EventCntrler(prefix='AS-Glob:TI-EVG:Linac')
    ev_ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
