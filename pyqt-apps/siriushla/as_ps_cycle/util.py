"""Utilities for ps-cycle."""
import numpy as np

import time as _time
import epics as _epics
from math import isclose as _isclose

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.search.ps_search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst


CONNECTION_TIMEOUT = 0.05


def get_manames():
    """."""
    return _MASearch.get_manames({'dis': 'MA'})


class Timing:
    """Timing."""

    DEFAULT_DURATION = 150  # [us]
    DEFAULT_NRPULSES = 1
    DEFAULT_DELAY = 0  # [us]
    DEFAULT_POLARITY = 'Normal'  # test

    _properties = {

        'RA-RaMO:TI-EVG:CycleMode-Sel': 'External',
        'RA-RaMO:TI-EVG:UpdateEvt-Cmd': 1,
        'RA-RaMO:TI-EVG:CycleExtTrig-Cmd': None,  # There is not default value

        'TB-Glob:TI-Mags:Src-Sel': 'Cycle',
        'TB-Glob:TI-Mags:NrPulses-SP': DEFAULT_NRPULSES,
        'TB-Glob:TI-Mags:Duration-SP': DEFAULT_DURATION,
        'TB-Glob:TI-Mags:Delay-SP': DEFAULT_DELAY,
        'TB-Glob:TI-Mags:Polarity-Sel': DEFAULT_POLARITY,  # test
        'TB-Glob:TI-Mags:State-Sel': 'Enbl',

        'BO-Glob:TI-Mags:Src-Sel': 'Cycle',
        'BO-Glob:TI-Mags:NrPulses-SP': DEFAULT_NRPULSES,
        'BO-Glob:TI-Mags:Duration-SP': DEFAULT_DURATION,
        'BO-Glob:TI-Mags:Delay-SP': DEFAULT_DELAY,
        'BO-Glob:TI-Mags:Polarity-Sel': DEFAULT_POLARITY,  # test
        'BO-Glob:TI-Mags:State-Sel': 'Enbl',

        'BO-Glob:TI-Corrs:Src-Sel': 'Cycle',
        'BO-Glob:TI-Corrs:NrPulses-SP': DEFAULT_NRPULSES,
        'BO-Glob:TI-Corrs:Duration-SP': DEFAULT_DURATION,
        'BO-Glob:TI-Corrs:Delay-SP': DEFAULT_DELAY,
        'BO-Glob:TI-Corrs:Polarity-Sel': DEFAULT_POLARITY,  # test
        'BO-Glob:TI-Corrs:State-Sel': 'Enbl',

    }

    _pvs = None

    def __init__(self):
        """Init."""
        self.init()

    @property
    def status_nok(self):
        """."""
        return self._status_nok.copy()

    def init(self):
        """Initialize timing properties.

        Return list with names of failing PVs.
        """
        if Timing._pvs is None:
            Timing._create_pvs()

        self._status_nok = []
        for prop, pv_defval in Timing._pvs.items():
            pv, defval = pv_defval
            pv.get()  # force connection
            if pv.connected:
                if defval is not None:
                    pv.value = defval
            else:
                self._status_nok.append(pv.pvname)

    def trigger(self):
        """Trigger timming."""
        if Timing._pvs is None:
            self._create_pvs()

        pv, _ = Timing._pvs['RA-RaMO:TI-EVG:CycleExtTrig-Cmd']
        pv.value = 1

    def _create_pvs():
        """."""
        # global _pvs_ti
        Timing._pvs = dict()
        for key, value in Timing._properties.items():
            Timing._pvs[key] = (
                _epics.PV(VACA_PREFIX + key,
                          connection_timeout=CONNECTION_TIMEOUT), value)


class MagnetCycler:
    """Handle magnet properties related to cycling."""

    def __init__(self, maname):
        """Constructor."""
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self.siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
        self.pwrstate_sel = _epics.get_pv(
            VACA_PREFIX + self._maname + ':PwrState-Sel')
        self.cycletype_sel = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleType-Sel')
        self.cyclefreq_sp = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleFreq-SP')
        self.cycleampl_sp = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleAmpl-SP')
        self.opmode_sel = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':OpMode-Sel')
        self.pwrstate_sts = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':PwrState-Sts')
        self.cycletype_sts = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleType-Sts')
        self.cyclefreq_rb = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleFreq-RB')
        self.cycleampl_rb = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleAmpl-RB')
        self.opmode_sts = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':OpMode-Sts')
        self.cycleenbl_mon = \
            _epics.get_pv(VACA_PREFIX + self._maname + ':CycleEnbl-Mon')

        self.pwrstate = 1

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    def set_on(self):
        """Turn magnet PS on."""
        return self.conn_put(self.pwrstate_sel, self.pwrstate)

    def set_params(self):
        """Set cycling params."""
        return (self.conn_put(self.cycletype_sel, self.siggen.type) and
                self.conn_put(self.cyclefreq_sp, self.siggen.freq) and
                self.conn_put(self.cycleampl_sp, self.siggen.amplitude))

    def set_mode(self):
        """Set magnet to cycling mode."""
        return self.conn_put(self.opmode_sel, _PSConst.OpMode.Cycle)

    def set_cycle(self):
        """Set magnet to cycling mode."""
        self.conn_put(self.opmode_sel, 0)
        self.set_on()
        _time.sleep(1e-2)
        self.set_params()
        _time.sleep(1e-2)
        self.set_mode()

    def on_rdy(self):
        """Return wether magnet PS is on."""
        return self.timed_get(self.pwrstate_sts, self.pwrstate)

    def params_rdy(self):
        """Return wether magnet cycling parameters are set."""
        return (self.timed_get(self.cycletype_sts, self.siggen.type) and
                self.timed_get(self.cyclefreq_rb, self.siggen.freq) and
                self.timed_get(self.cycleampl_rb, self.siggen.amplitude))

    def mode_rdy(self):
        """Return wether magnet is in cycling mode."""
        return self.timed_get(self.opmode_sts, _PSConst.States.Cycle)

    def is_ready(self):
        """Return wether magnet is ready to cycle."""
        return self.on_rdy() and self.params_rdy() and self.mode_rdy()

    def conn_put(self, pv, value):
        """Put if connected."""
        if not pv.connected:
            return False
        if pv.put(value):
            return True
        return False

    def timed_get(self, pv, value, wait=20):
        """Do timed get."""
        if not pv.connected:
            return False
        t = 0
        init = _time.time()
        while t < wait:
            if isinstance(value, float):
                if _isclose(pv.get(), value, rel_tol=1e-06, abs_tol=0.0):
                    return True

            else:
                v = pv.get()
                if isinstance(v, np.ndarray):
                    if np.all(v == value):
                        return True
                else:
                    if v == value:
                        return True
                # if pv.get() == value:
                #     return True
            t = _time.time() - init
            _time.sleep(5e-3)
        return False
