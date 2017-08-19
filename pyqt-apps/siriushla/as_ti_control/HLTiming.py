"""Control of EVG Timing Device."""

import sys as _sys
import os as _os
from PyQt5 import uic as _uic
from PyQt5.QtWidgets import QGridLayout as _QGridLayout
from PyQt5.QtWidgets import QGroupBox as _QGroupBox
from PyQt5.QtWidgets import QVBoxLayout as _QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy as _QSzPol
from PyQt5.QtWidgets import QSpacerItem as _QSpIt
from pydm import PyDMApplication as _PyDMApplication
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.timesys.time_data import Clocks as _Clocks
from siriuspy.timesys.time_data import Events as _Events
from siriuspy.timesys.time_data import Triggers as _Triggers
from siriushla.as_ti_control.Controllers import IntTrigCntrler, OutChanCntrler
from siriushla.as_ti_control.Controllers import (EventCntrler, HLTrigCntrler,
                                                 ClockCntrler)

_dir = _os.path.dirname(_os.path.abspath(__file__))
UI_FILE = _os.path.sep.join([_dir, 'TimingMain.ui'])


def main(prefix=None):
    """Setup the main window."""
    prefix = 'ca://' + (prefix or PREFIX)
    hl_trigs = _Triggers().hl_triggers
    HLTiming = _uic.loadUi(UI_FILE)
    # HLTiming.setStyleSheet('font-size: 21px')
    _setupEvents(prefix, HLTiming)
    _setupClocks(prefix, HLTiming)
    _setupEVGParams(prefix, HLTiming)
    _setupTriggers(prefix, HLTiming, hl_trigs)
    return HLTiming


def _setupTrigs(prefix, main, map_, hl_trigs, nc=1, hide_evg=False):
    lv = _QVBoxLayout()
    # lv.setSpacing(0)
    main.setLayout(lv)
    lv.addItem(_QSpIt(40, 20, _QSzPol.Minimum, _QSzPol.Expanding))
    for k, v in map_.items():
        gb = _QGroupBox(k, main)
        lv.addWidget(gb)
        lv.addItem(_QSpIt(40, 20, _QSzPol.Minimum, _QSzPol.Expanding))
        lg = _QGridLayout()
        gb.setLayout(lg)
        lg.setVerticalSpacing(0)
        for i, tr in enumerate(v):
            pref = prefix + tr
            if hide_evg:
                props = hl_trigs[tr]['hl_props'] - {'evg_param'}
            else:
                props = hl_trigs[tr]['hl_props']
            trig = HLTrigCntrler(prefix=pref, props=props)
            lg.addWidget(trig, (i // nc) + 1, i % nc)
            if i // nc:
                continue
            header = HLTrigCntrler(prefix=pref, props=props, header=True)
            lg.addWidget(header, 0, i % nc)


def _setupTriggers(prefix, HLTiming, hl_trigs):
    map_ = {
        'Linac': (
            'LI-01:TI-EGun:MultBun', 'LI-01:TI-EGun:SglBun',
            'LI-01:TI-Modltr-1:', 'LI-01:TI-Modltr-2:',
            'LI-Glob:TI-LLRF-1:', 'LI-Glob:TI-LLRF-2:',
            'LI-Glob:TI-LLRF-3:', 'LI-Glob:TI-RFAmp-1:',
            'LI-Glob:TI-RFAmp-2:', 'LI-Glob:TI-SHAmp:'),
        'Booster Injection': ('TB-04:TI-InjS:', 'BO-01D:TI-InjK:'),
        }
    main = HLTiming.WDTrigsInjLITB
    _setupTrigs(prefix, main, map_, hl_trigs, 2)

    map_ = {
        'Booster Ramping': ('BO-05D:TI-P5Cav:', 'BO-Glob:TI-Mags:'),
        'Storage Ring Injection': (
            'BO-48D:TI-EjeK:', 'TS-04:TI-InjSF:',
            'TS-Fam:TI-EjeS:', 'TS-Fam:TI-InjSG:',
            'SI-01SA:TI-InjK:'),
        }
    main = HLTiming.WDTrigsInjBOSI
    _setupTrigs(prefix, main, map_, hl_trigs, 2)

    map_ = {
        'Linac': (
            'LI-01:TI-ICT-1:', 'LI-01:TI-ICT-2:',
            'LI-Fam:TI-BPM:', 'LI-Fam:TI-Scrn:'),
        'Booster Transfer Line': (
            'TB-02:TI-ICT:', 'TB-04:TI-FCT:', 'TB-04:TI-ICT:',
            'TB-Fam:TI-BPM:', 'TB-Fam:TI-Scrn:'),
        'Booster': (
            'BO-02D:TI-TuneS:', 'BO-04D:TI-TuneP:', 'BO-04U:TI-GSL:',
            'BO-35D:TI-DCCT:', 'BO-Fam:TI-BPM:', 'BO-Fam:TI-Scrn:'),
        'Storage Ring Injection': (
            'TS-01:TI-ICT:', 'TS-04:TI-FCT:', 'TS-04:TI-ICT:',
            'TS-Fam:TI-BPM:', 'TS-Fam:TI-Scrn:',
            'SI-Fam:TI-BPM:'),
        }
    main = HLTiming.WDTrigsInjDig
    _setupTrigs(prefix, main, map_, hl_trigs)

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
    main = HLTiming.WDTrigsSI
    _setupTrigs(prefix, main, map_, hl_trigs)


def _setupEVGParams(prefix, HLTiming):
    pv_pref = prefix + 'AS-Glob:TI-EVG:'
    HLTiming.PyDMLEBucketList.channel = pv_pref + 'BucketList-SP'
    HLTiming.PyDMLbBucketList.channel = pv_pref + 'BucketList-RB'
    HLTiming.PyDMStBContinuous.channel = pv_pref + 'ContinuousState-Sel'
    HLTiming.PyDMLedContinuous.channel = pv_pref + 'ContinuousState-Sts'
    HLTiming.PyDMStBInjectionState.channel = pv_pref + 'InjectionState-Sel'
    HLTiming.PyDMLedInjectionState.channel = pv_pref + 'InjectionState-Sts'
    HLTiming.PyDMCbInjectionCyc.channel = pv_pref + 'InjectionCyc-Sel'
    HLTiming.PyDMLedInjectionCyc.channel = pv_pref + 'InjectionCyc-Sts'
    HLTiming.PyDMSBRepetitionRate.channel = pv_pref + 'RepRate-SP'
    HLTiming.PyDMLbRepetitionRate.channel = pv_pref + 'RepRate-RB'


def _setupClocks(prefix, HLTiming):
    main = HLTiming.DWCClocks
    lg = _QGridLayout(main)
    main.setLayout(lg)
    props = {'state', 'frequency'}
    for i, cl in enumerate(sorted(_Clocks.HL2LL_MAP.keys())):
        pref = prefix + _Clocks.HL_PREF + cl
        if i == 0:
            lg.addWidget(ClockCntrler(prefix=pref, props=props,
                                      header=True), 0, 0)
        lg.addWidget(ClockCntrler(prefix=pref, props=props), i + 1, 0)


def _setupEvents(prefix, HLTiming):
    map_ = {
        'Injection': ('Linac', 'InjBO', 'RmpBO', 'InjSI'),
        'Diagnostics': ('DigLI', 'DigTB', 'DigBO', 'DigTS', 'DigSI'),
        'Storage Ring Control': ('Orbit', 'Tunes', 'Coupl', 'Study'),
        }
    main = HLTiming.DWCEvents

    lv = _QVBoxLayout()
    main.setLayout(lv)
    lv.addItem(_QSpIt(40, 20, _QSzPol.Minimum, _QSzPol.Expanding))
    nc = 1
    props = {'ext_trig', 'mode', 'delay'}
    for k, v in map_.items():
        gb = _QGroupBox(k, main)
        lv.addWidget(gb)
        lv.addItem(_QSpIt(40, 20, _QSzPol.Minimum, _QSzPol.Expanding))
        lg = _QGridLayout()
        gb.setLayout(lg)
        for i, ev in enumerate(v):
            pref = prefix + _Events.HL_PREF + ev
            if not i // nc:
                header = EventCntrler(prefix=pref, props=props, header=True)
                lg.addWidget(header, 0, i % nc)
            ev_ctrl = EventCntrler(prefix=pref, props=props)
            lg.addWidget(ev_ctrl, (i // nc) + 1, i % nc)


if __name__ == '__main__':
    """Run Example."""
    app = _PyDMApplication()
    HLTiming = main()
    HLTiming.show()
    _sys.exit(app.exec_())
