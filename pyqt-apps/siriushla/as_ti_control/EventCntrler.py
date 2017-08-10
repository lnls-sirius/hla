import sys
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinBox
from pydm.widgets.pushbutton import PyDMPushButton
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

PREFIX = 'fac' + PREFIX[8:]


class EventCntrler(QGroupBox):
    """Template for control of High and Low Level Events."""

    def __init__(self, parent=None, prefix='', tp='ll'):
        """Initialize the instance."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.event_type = tp
        self._setupUi()

    def _setupUi(self):
        pv_pref = 'ca://' + PREFIX + self.prefix
        lh = QHBoxLayout(self)
        self.setLayout(lh)
        self.setTitle(self.prefix.propty)

        # lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))

        # External Trigger
        pb = PyDMPushButton(self, init_channel=pv_pref+'ExtTrig-Cmd',
                            pressValue=1)
        pb.setText('< External >')
        lh.addWidget(pb)
        # lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))

        # Control of event Mode
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Mode Selection', self))
        lv.addWidget(PyDMECB(self, init_channel=pv_pref + "Mode-Sel"))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Mode-Sts"))
        lh.addItem(lv)
        # lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))

        # Control of DelayType
        if self.event_type == 'll':
            lv = QVBoxLayout()
            lv.addWidget(QLabel('Delay Type', self))
            lv.addWidget(PyDMECB(self, init_channel=pv_pref+"DelayType-Sel"))
            lv.addWidget(PyDMLabel(self, init_channel=pv_pref+"DelayType-Sts"))
            lh.addItem(lv)
            # lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))

        # Control of Delay
        lv = QVBoxLayout()
        lv.addWidget(QLabel('Delay [us]', self))
        lv.addWidget(PyDMSpinBox(self,
                                 init_channel=pv_pref + "Delay-SP",
                                 step=1e-3, limits_from_pv=True))
        lv.addWidget(PyDMLabel(self, init_channel=pv_pref + "Delay-RB",
                               prec_from_pv=True))
        lh.addItem(lv)
        # lh.addItem(QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum))


def main():
    """Run Example."""
    app = PyDMApplication()
    ev_ctrl = EventCntrler(prefix='AS-Glob:TI-EVG:Linac')
    ev_ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
