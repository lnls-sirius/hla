"""Control of EVG Timing Device."""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from pydm import PyDMApplication
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.timesys import time_data
from siriuspy.timesys.time_data import Clocks as _Clocks
from siriuspy.timesys.time_data import Events as _Events
from siriuspy.timesys.time_data import Triggers as _Triggers
from siriushla.as_ti_control.ClockCntrler import ClockCntrler
from siriushla.as_ti_control.EventCntrler import EventCntrler
from siriushla.as_ti_control.HLTrigCntrler import HLTrigCntrler

time_data._LOCAL = True

PREFIX = 'fac' + PREFIX[8:]
HLTriggers = None


def _setupTrigs(main, map_, nc, hide_evg=True):
        lv = QVBoxLayout()
        main.setLayout(lv)
        lv.addItem(QSpIt(40, 20, QSzPol.Minimum, QSzPol.Expanding))
        for k, v in map_.items():
            gb = QGroupBox(k, main)
            lv.addWidget(gb)
            lv.addItem(QSpIt(40, 20, QSzPol.Minimum, QSzPol.Expanding))
            lg = QGridLayout()
            gb.setLayout(lg)
            for i, tr in enumerate(v):
                if hide_evg:
                    hl_props = HLTriggers[tr]['hl_props'] - {'evg_param'}
                else:
                    hl_props = HLTriggers[tr]['hl_props']
                lg.addWidget(HLTrigCntrler(prefix=tr, hl_props=hl_props),
                             i // nc, i % nc)


def _setupTriggers(HLTiming):
    map_ = {
        'Linac': (
            'LI-01:TI-EGun:MultBun', 'LI-01:TI-EGun:SglBun',
            'LI-01:TI-Modltr-1:', 'LI-01:TI-Modltr-2:',
            'LI-Glob:TI-LLRF-1:', 'LI-Glob:TI-LLRF-2:',
            'LI-Glob:TI-LLRF-3:', 'LI-Glob:TI-RFAmp-1:',
            'LI-Glob:TI-RFAmp-2:', 'LI-Glob:TI-SHAmp:'),
        'Booster Injection': ('TB-04:TI-InjS:', 'BO-01D:TI-InjK:'),
        }
    _setupTrigs(HLTiming.WDTrigsInjLITB, map_, 2, hide_evg=True)
    map_ = {
        'Booster Ramping': ('BO-05D:TI-P5Cav:', 'BO-Glob:TI-Mags:'),
        'Storage Ring Injection': (
            'BO-48D:TI-EjeK:', 'TS-04:TI-InjSF:',
            'TS-Fam:TI-EjeS:', 'TS-Fam:TI-InjSG:',
            'SI-01SA:TI-InjK:'),
        }
    _setupTrigs(HLTiming.WDTrigsInjBOSI, map_, 2, hide_evg=True)

    map_ = {
        'Linac': (
            'LI-01:TI-ICT-1:', 'LI-01:TI-ICT-2:',
            'LI-Fam:TI-BPM:', 'LI-Fam:TI-Scrn:'),
        'Booster Injection': (
            'TB-02:TI-ICT:', 'TB-04:TI-FCT:', 'TB-04:TI-ICT:',
            'TB-Fam:TI-BPM:', 'TB-Fam:TI-Scrn:',
            'BO-02D:TI-TuneS:', 'BO-04D:TI-TuneP:', 'BO-04U:TI-GSL:',
            'BO-35D:TI-DCCT:', 'BO-Fam:TI-BPM:', 'BO-Fam:TI-Scrn:'),
        'Storage Ring Injection': (
            'TS-01:TI-ICT:', 'TS-04:TI-FCT:', 'TS-04:TI-ICT:',
            'TS-Fam:TI-BPM:', 'TS-Fam:TI-Scrn:',
            'SI-Fam:TI-BPM:'),
        }
    _setupTrigs(HLTiming.WDTrigsInjDig, map_, 1, hide_evg=False)
    map_ = {
        'Storage Ring Studies': (
            'SI-01SA:TI-HPing:', 'SI-01SA:TI-HTuneS:', 'SI-13C4:TI-DCCT:',
            'SI-14C4:TI-DCCT:', 'SI-16C4:TI-GBPM:', 'SI-17C4:TI-VTuneP:',
            'SI-17SA:TI-HTuneP:', 'SI-18C4:TI-VTuneS:', 'SI-19C4:TI-VPing:',
            'SI-19SP:TI-GSL15:', 'SI-20SB:TI-GSL07:'),
        'Storage Ring Magnets': (
            'SI-Glob:TI-Corrs:', 'SI-Glob:TI-Dips:', 'SI-Glob:TI-Quads:',
            'SI-Glob:TI-Sexts:', 'SI-Glob:TI-Skews:',
            )
        }
    _setupTrigs(HLTiming.WDTrigsSI, map_, 1, hide_evg=True)


def _setupEVGParams(HLTiming):
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


def _setupClocks(HLTiming):
    main = HLTiming.DWCClocks
    lg = QGridLayout(main)
    main.setLayout(lg)
    for i, cl in enumerate(sorted(_Clocks.HL2LL_MAP.keys())):
        pref = _Clocks.HL_PREF + cl
        lg.addWidget(ClockCntrler(main, prefix=pref), i, 0)


def _setupEvents(HLTiming):
    map_ = {
        'Injection': ('Linac', 'InjBO', 'RmpBO', 'InjSI'),
        'Diagnostics': ('DigLI', 'DigTB', 'DigBO', 'DigTS', 'DigSI'),
        'Storage Ring Control': ('Orbit', 'Tunes', 'Coupl', 'Study'),
        }
    main = HLTiming.DWCEvents

    lv = QVBoxLayout()
    main.setLayout(lv)
    lv.addItem(QSpIt(40, 20, QSzPol.Minimum, QSzPol.Expanding))
    nc = 1
    for k, v in map_.items():
        gb = QGroupBox(k, main)
        lv.addWidget(gb)
        lv.addItem(QSpIt(40, 20, QSzPol.Minimum, QSzPol.Expanding))
        lg = QGridLayout()
        gb.setLayout(lg)
        for i, ev in enumerate(v):
            pref = _Events.HL_PREF + ev
            ev_ctrl = EventCntrler(main, prefix=pref, tp='hl')
            lg.addWidget(ev_ctrl, i // nc, i % nc)


def setupMainWindow():
    global HLTriggers
    HLTriggers = _Triggers().hl_triggers
    HLTiming = uic.loadUi('HLTiming.ui')
    # HLTiming.setStyleSheet('font: 12pt "Sans Serif";')
    _setupEvents(HLTiming)
    _setupClocks(HLTiming)
    _setupEVGParams(HLTiming)
    _setupTriggers(HLTiming)
    return HLTiming


def main():
    """Run Example."""
    app = PyDMApplication()
    HLTiming = setupMainWindow()
    HLTiming.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
