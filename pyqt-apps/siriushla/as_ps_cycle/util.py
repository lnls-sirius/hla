"""Utilities for ps-cycle."""
import numpy as np

import time as _time
import epics as _epics
from math import isclose as _isclose

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.search.ps_search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ETypes as _et


CONNECTION_TIMEOUT = 0.05
SLEEP_CAPUT = 0.1


_pvs = dict()


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

    _properties = [
        'PwrState-Sel', 'PwrState-Sts',
        'OpMode-Sel', 'OpMode-Sts',
        'CycleType-Sel', 'CycleType-Sts',
        'CycleFreq-SP', 'CycleFreq-RB',
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleAuxParam-SP', 'CycleAuxParam-RB',
        'CycleEnbl-Mon',
    ]

    def __init__(self, maname):
        """Constructor."""
        global _pvs
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self.siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
        # self._pvs = dict()
        for prop in MagnetCycler._properties:
            pvname = self._get_pvname(prop)
            if pvname not in _pvs:
                _pvs[prop] = \
                    _epics.PV(pvname, connection_timeout=CONNECTION_TIMEOUT)

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    @property
    def connected(self):
        """Return connected state."""
        for prop in MagnetCycler._properties:
            pvname = self._get_pvname(prop)
            if not _pvs[pvname].connected:
                return False
        return True

    def set_on(self):
        """Turn magnet PS on."""
        pvname = self._get_pvname('PwrState-Sel')
        return self.conn_put(_pvs[pvname], _PSConst.PwrStateSel.On)

    def __getitem__(self, prop):
        """."""
        pvname = self._get_pvname(prop)
        return _pvs[pvname]

    def set_cycle_params(self):
        """Set cycling params."""
        status = True
        status &= self.conn_put(_pvs[self._get_pvname('CycleType-Sel')],
                                self.siggen.type)
        _time.sleep(SLEEP_CAPUT)
        status &= self.conn_put(_pvs[self._get_pvname('CycleFreq-SP')],
                                self.siggen.freq)
        _time.sleep(SLEEP_CAPUT)
        status &= self.conn_put(_pvs[self._get_pvname('CycleAmpl-SP')],
                                self.siggen.amplitude)
        _time.sleep(SLEEP_CAPUT)
        status &= self.conn_put(_pvs[self._get_pvname('CycleAuxParam-SP')],
                                self.siggen.aux_param)

    def set_mode(self, opmode):
        """Set magnet to opmode."""
        if opmode not in _et.OPMODES:
            return False
        else:
            return self.conn_put(_pvs[self._get_pvname('OpMode-Sel')], opmode)

    def config_cycle(self):
        """Config magnet to cycling mode."""
        status = True

        status &= self.set_mode(_PSConst.OpMode.SlowRef)
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_on()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_cycle_params()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_mode(_PSConst.OpMode.Cycle)

        return status

    def config_rmpwfm(self):
        """Config magnet to rmpwfm mode."""
        status = True

        status &= self.set_mode(_PSConst.OpMode.SlowRef)
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_on()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_mode(_PSConst.OpMode.Cycle)

        return status

    def on_rdy(self):
        """Return wether magnet PS is on."""
        pvname = self._get_pvname('PwrState-Sts')
        status = self.timed_get(_pvs[pvname], _PSConst.PwrStateSts.On)
        return status

    def params_rdy(self):
        """Return wether magnet cycling parameters are set."""
        status = True

        pvname = self._get_pvname('CycleType-Sts')
        type_idx = _et.CYCLE_TYPES.index(self.siggen.type)
        status &= self.timed_get(_pvs[pvname], type_idx)

        pvname = self._get_pvname('CycleFreq-RB')
        status &= self.timed_get(_pvs[pvname], self.siggen.freq)

        pvname = self._get_pvname('CycleAmpl-RB')
        status &= self.timed_get(_pvs[pvname], self.siggen.amplitude)

        pvname = self._get_pvname('CycleAuxParam-RB')
        status &= self.timed_get(_pvs[pvname], self.siggen.aux_param)

        return status

    def mode_rdy(self, opmode):
        """Return wether magnet is in opmode."""
        if opmode not in _et.OPMODES:
            return False
        pvname = self._get_pvname('OpMode-Sts')
        return self.timed_get(_pvs[pvname], opmode)

    def is_ready(self, opmode):
        """Return wether magnet is ready."""
        status = self.on_rdy() and self.mode_rdy(opmode)
        if opmode == 'Cycle':
            status &= self.params_rdy()
        return status

    def conn_put(self, pv, value):
        """Put if connected."""
        if not pv.connected:
            return False
        if pv.put(value):
            return True
        return False

    def timed_get(self, pv, value, wait=1.0):
        """Do timed get."""
        if not pv.connected:
            return False
        t0 = _time.time()
        while _time.time() - t0 < wait:
            pvvalue = pv.get()
            status = False
            if isinstance(value, (tuple, list, np.ndarray)):
                if not isinstance(pvvalue, (tuple, list, np.ndarray)):
                    status = False
                if len(value) != len(pvvalue):
                    status = False
                for i in range(len(value)):
                    if _isclose(pvvalue[i], value[i],
                                rel_tol=1e-06, abs_tol=0.0):
                        status = True
                    else:
                        status = False
            else:
                if _isclose(pvvalue[i], value[i],
                            rel_tol=1e-06, abs_tol=0.0):
                    status = True
                else:
                    status = False
            _time.sleep(wait/10.0)
        return status

    def _get_pvname(self, prop):
        """."""
        return VACA_PREFIX + self._maname + ':' + prop
