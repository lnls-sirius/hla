"""Control of EVG Timing Device."""

import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox
from pydm.widgets.label import PyDMLabel
from pydm.widgets.led import PyDMLed
from pydm.widgets.spinbox import PyDMSpinBox
from siriuspy.timesys.time_data import Clocks as _Clocks
from siriuspy.timesys.time_data import Events as _Events
from siriushla.as_ti_control.Controllers import ClockCntrler, EventCntrler


class EVGCntrler(QWidget):
    """Control for EVG."""

    def __init__(self):
        """Initialize Instance."""
        super().__init__()
        self._setupUi()

    def _setupUi(self):
        self.setObjectName("EVG")
        self.resize(1636, 1471)

        lg = QGridLayout(self)
        self.setLayout(lg)
        self.GBClocks = QGroupBox("Clocks", self)
        lg.addWidget(self.GBClocks, 2, 0)
        self._setupGBClocks()

        spol = QSzPol(QSzPol.Preferred, QSzPol.Preferred)
        spol.setHorizontalStretch(1)
        spol.setVerticalStretch(0)
        gb_ev = QGroupBox('Events', self)
        # spol.setHeightForWidth(gb_ev.sizePolicy().hasHeightForWidth())
        gb_ev.setSizePolicy(spol)
        lg.addWidget(gb_ev, 0, 1, 3, 1)
        lv = QVBoxLayout(gb_ev)
        sa_ev = QScrollArea(gb_ev)
        lv.addWidget(sa_ev)
        sa_ev.setWidgetResizable(True)
        self.WDEvents = QWidget()
        # wid_ev.setGeometry(QtCore.QRect(0, 0, 780, 1309))
        sa_ev.setWidget(self.WDEvents)
        self._setupGBEvents()

        self.GBTables = QGroupBox(self)
        self.GBTables.setSizePolicy(spol)
        lg.addWidget(self.GBTables, 1, 0)
        self.GBControl = QGroupBox(self)
        self.gridLayout_2 = QGridLayout(self.GBControl)
        self.PyDMCbselfEnable = PyDMCheckbox(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMCbselfEnable, 0, 1, 1, 1)
        self.PyDMLedselfEnable = PyDMLed(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMLedselfEnable, 0, 0, 1, 1)
        self.PyDMLed = PyDMLed(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMLed, 1, 0, 1, 1)
        self.PyDMCbTableEnable = PyDMCheckbox(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMCbTableEnable, 0, 4, 1, 1)
        self.PyDMSpinBox = PyDMSpinBox(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMSpinBox, 1, 2, 1, 1)
        self.PyDMLedTableEnable = PyDMLed(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMLedTableEnable, 0, 3, 1, 1)
        self.PyDMCheckbox = PyDMCheckbox(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMCheckbox, 1, 1, 1, 1)
        spacerItem = QSpIt(40, 20, QSzPol.Expanding, QSzPol.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.PyDMLabel = PyDMLabel(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMLabel, 1, 3, 1, 1)
        self.PyDMLbTableStatus = PyDMLabel(self.GBControl)
        self.gridLayout_2.addWidget(self.PyDMLbTableStatus, 0, 5, 1, 1)
        lg.addWidget(self.GBControl, 0, 0)

        self.setWindowTitle("Form")
        self.GBTables.setTitle("Tables")
        self.GBControl.setTitle("Control")
        self.PyDMCbselfEnable.setText("Enable EVG")
        self.PyDMCbTableEnable.setText("Enable Tables")
        self.PyDMCheckbox.setText("AC Line Enable")
        self.PyDMLbTableStatus.setText("STATUS")

    def _setupGBClocks(self):
        lg = QGridLayout(self)
        self.GBClocks.setLayout(lg)
        for i, cl in enumerate(sorted(_Clocks.LL2HL_MAP.keys())):
            pref = _Clocks.HL_PREF + cl
            clock = ClockCntrler(prefix=pref, hl_props=hl_props)
            lg.addWidget(clock, i % 4, i//4)

    def _setupGBEvents(self):
        lg = QGridLayout(self)
        self.WDEvents.setLayout(lg)
        for i, ev in enumerate(_Events.LL_EVENTS):
            pref = _Events.HL_PREF + ev
            lg.addWidget(EventCntrler(self, prefix=pref), i // 2, i % 2)


def main():
    """Run Example."""
    app = PyDMApplication()
    # ctrl = OutChanCntrler(prefix='AS-Glob:TI-EVR-1:OUT0', device='evr')
    ctrl = EVGCntrler()
    ctrl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
