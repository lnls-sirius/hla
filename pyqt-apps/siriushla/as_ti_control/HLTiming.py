"""Control of EVG Timing Device."""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from pydm import PyDMApplication
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.timesys.time_data import Clocks as _Clocks
from siriuspy.timesys.time_data import Events as _Events
from siriushla.as_ti_control.ClockCntrler import ClockCntrler
from siriushla.as_ti_control.EventCntrler import EventCntrler

PREFIX = 'fac' + PREFIX[8:]


def setupEVGParams(HLTiming):
    pv_pref = 'ca://' + PREFIX + 'AS-Glob:TI-EVG:'
    HLTiming.PyDMLEBucketList.channel = pv_pref + 'BucketList-SP'
    HLTiming.PyDMLbBucketList.channel = pv_pref + 'BucketList-RB'
    HLTiming.PyDMCbContinuous.channel = pv_pref + 'ContinuousState-Sel'
    HLTiming.PyDMLedContinuous.channel = pv_pref + 'ContinuousState-Sts'
    HLTiming.PyDMCbInjectionState.channel = pv_pref + 'InjectionState-Sel'
    HLTiming.PyDMLedInjectionState.channel = pv_pref + 'InjectionState-Sts'
    HLTiming.PyDMCbInjectionCyc.channel = pv_pref + 'InjectionCyc-Sel'
    HLTiming.PyDMLedInjectionCyc.channel = pv_pref + 'InjectionCyc-Sts'
    HLTiming.PyDMSBRepetitionRate.channel = pv_pref + 'RepRate-SP'
    HLTiming.PyDMLbRepetitionRate.channel = pv_pref + 'RepRate-RB'


def setupClocks(HLTiming):
    main = HLTiming.DWCClocks
    lg = QGridLayout(main)
    main.setLayout(lg)
    for i, cl in enumerate(sorted(_Clocks.HL2LL_MAP.keys())):
        pref = _Clocks.HL_PREF + cl
        lg.addWidget(ClockCntrler(main, prefix=pref), i, 0)


def setupEvents(HLTiming):
    main = HLTiming.DWCEvents
    lg = QGridLayout()
    main.setLayout(lg)
    for i, ev in enumerate(sorted(_Events.HL2LL_MAP.keys())):
        pref = _Events.HL_PREF + ev
        lg.addWidget(EventCntrler(main, prefix=pref), i, 0)


def main():
    """Run Example."""
    app = PyDMApplication()
    # ctrl = OutChanCntrler(prefix='AS-Glob:TI-EVR-1:OUT0', device='evr')
    HLTiming = uic.loadUi('HLTiming.ui')
    setupEvents(HLTiming)
    setupClocks(HLTiming)
    setupEVGParams(HLTiming)
    HLTiming.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
