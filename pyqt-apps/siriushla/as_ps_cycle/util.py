"""Utilities for ps-cycle."""
import numpy as np

import time as _time
from epics import PV as _PV
from math import isclose as _isclose
import numpy as _np

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.timesys import Const as _TIConst
from siriuspy.csdevice.pwrsupply import ETypes as _PSet
from siriushla.as_ps_cycle.ramp_data import BASE_RAMP_CURVE_ORIG as \
    _BASE_RAMP_CURVE_ORIG


TIMEOUT = 0.05
SLEEP_CAPUT = 0.1


def get_manames():
    """Return manames."""
    return _MASearch.get_manames({'sec': '(SI|TS|BO|TB)', 'dis': 'MA'})


def get_manames_from_same_udc(maname):
    """Return manames that are controled by same udc as maname."""
    psname = _MASearch.conv_maname_2_psnames(maname)[0]
    udc = _PSSearch.conv_psname_2_udc(psname)
    bsmp_list = _PSSearch.conv_udc_2_bsmps(udc)
    psnames = [bsmp[0] for bsmp in bsmp_list]
    manames = set([_MASearch.conv_psname_2_psmaname(name) for name in psnames])
    return manames


def _generate_base_wfmdata():
    t0 = _BASE_RAMP_CURVE_ORIG[:, 0]
    w0 = _BASE_RAMP_CURVE_ORIG[:, 1]
    nrpulses = Timing.DEFAULT_RMPBO_NRPULSES
    duration = Timing.DEFAULT_RMPBO_DURATION/1000.0
    t = _np.linspace(0.0, duration, nrpulses)
    w = _np.interp(t, t0, w0)
    return w


class Timing:
    """Timing."""

    EVTNAME_CYCLE = 'Cycle'
    EVTNAME_RAMP = 'RmpBO'

    DEFAULT_CYCLE_DURATION = 150  # [us]
    DEFAULT_CYCLE_NRPULSES = 1
    DEFAULT_RMPBO_DURATION = 490000  # [us]
    DEFAULT_RMPBO_NRPULSES = 4000
    DEFAULT_DELAY = 0  # [us]
    DEFAULT_POLARITY = _TIConst.TrigPol.Normal  # test
    DEFAULT_STATE = _TIConst.DsblEnbl.Enbl

    DEFAULT_RAMP_NRCYCLES = 16
    DEFAULT_RAMP_TOTDURATION = DEFAULT_RMPBO_DURATION * \
        DEFAULT_RAMP_NRCYCLES/1000000  # [s]

    properties = {
        'Demag': {
            # EVG settings
            'RA-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'RA-RaMO:TI-EVG:UpdateEvt-Cmd': 1,

            # Cycle event settings
            'RA-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.External,
            'RA-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Fixed,
            'RA-RaMO:TI-EVG:CycleExtTrig-Cmd': 1,  # There is no default value

            # TB magnets trigger settings
            'TB-Glob:TI-Mags:Src-Sel': EVTNAME_CYCLE,
            'TB-Glob:TI-Mags:Duration-SP': DEFAULT_CYCLE_DURATION,
            'TB-Glob:TI-Mags:NrPulses-SP': DEFAULT_CYCLE_NRPULSES,
            'TB-Glob:TI-Mags:Delay-SP': DEFAULT_DELAY,
            'TB-Glob:TI-Mags:Polarity-Sel': DEFAULT_POLARITY,
            'TB-Glob:TI-Mags:State-Sel': DEFAULT_STATE,

            # BO magnets trigger settings
            'BO-Glob:TI-Mags:Src-Sel': EVTNAME_CYCLE,
            'BO-Glob:TI-Mags:Duration-SP': DEFAULT_CYCLE_DURATION,
            'BO-Glob:TI-Mags:NrPulses-SP': DEFAULT_CYCLE_NRPULSES,
            'BO-Glob:TI-Mags:Delay-SP': DEFAULT_DELAY,
            'BO-Glob:TI-Mags:Polarity-Sel': DEFAULT_POLARITY,
            'BO-Glob:TI-Mags:State-Sel': DEFAULT_STATE,

            # BO correctors trigger settings
            'BO-Glob:TI-Corrs:Src-Sel': EVTNAME_CYCLE,
            'BO-Glob:TI-Corrs:Duration-SP': DEFAULT_CYCLE_DURATION,
            'BO-Glob:TI-Corrs:NrPulses-SP': DEFAULT_CYCLE_NRPULSES,
            'BO-Glob:TI-Corrs:Delay-SP': DEFAULT_DELAY,
            'BO-Glob:TI-Corrs:Polarity-Sel': DEFAULT_POLARITY,
            'BO-Glob:TI-Corrs:State-Sel': DEFAULT_STATE,
        },
        'Cycle': {
            # EVG settings
            'RA-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'RA-RaMO:TI-EVG:ContinuousEvt-Sel': DEFAULT_STATE,

            # Ramp event settings
            'RA-RaMO:TI-EVG:RmpBOMode-Sel': None,
            'RA-RaMO:TI-EVG:RmpBODelayType-Sel': _TIConst.EvtDlyTyp.Incr,
            'RA-RaMO:TI-EVG:RmpBODelay-SP': DEFAULT_DELAY,

            # BO magnets trigger settings
            'BO-Glob:TI-Mags:Src-Sel': EVTNAME_RAMP,
            'BO-Glob:TI-Mags:Duration-SP': DEFAULT_RMPBO_DURATION,
            'BO-Glob:TI-Mags:NrPulses-SP': DEFAULT_RMPBO_NRPULSES,
            'BO-Glob:TI-Mags:Delay-SP': DEFAULT_DELAY,
            'BO-Glob:TI-Mags:Polarity-Sel': DEFAULT_POLARITY,
            'BO-Glob:TI-Mags:State-Sel': DEFAULT_STATE,
        }
    }

    _pvs = None

    def __init__(self):
        """Init."""
        self._create_pvs()
        self._status_nok = []

    @property
    def status_nok(self):
        """Return list with names of failing PVs."""
        return self._status_nok.copy()

    def init(self, mode):
        """Initialize properties."""
        for prop, defval in Timing.properties[mode].items():
            pv = Timing._pvs[prop]
            pv.get()  # force connection
            if pv.connected and defval is not None:
                pv.value = defval

    @property
    def connected(self):
        """Return connected state."""
        self._status_nok = []
        for pv in Timing._pvs.values():
            if not pv.connected:
                self._status_nok.append(pv.pvname)
        return not bool(self._status_nok)

    def trigger2demag(self):
        """Trigger timming to cycle magnets."""
        pv = Timing._pvs['RA-RaMO:TI-EVG:CycleExtTrig-Cmd']
        pv.value = 1

    def init_ramp(self):
        """."""
        pv = Timing._pvs['RA-RaMO:TI-EVG:RmpBOMode-Sel']
        pv.value = _TIConst.EvtModes.Continuous

    def finish_ramp(self):
        """."""
        pv = Timing._pvs['RA-RaMO:TI-EVG:RmpBOMode-Sel']
        pv.value = _TIConst.EvtModes.Disabled

    def _create_pvs(self):
        """Create PVs."""
        Timing._pvs = dict()
        for mode, dict_ in Timing.properties.items():
            for pvname in dict_.keys():
                Timing._pvs[pvname] = _PV(VACA_PREFIX+pvname,
                                          connection_timeout=TIMEOUT)
                Timing._pvs[pvname].get()


class MagnetCycler:
    """Handle magnet properties related to Cycle and RmpWfm ps modes."""

    RAMP_AMPLITUDE = {  # A
        'BO-Fam:MA-B':  1100,
        'BO-Fam:MA-QD': 30,
        'BO-Fam:MA-QF': 130,
        'BO-Fam:MA-SD': 150,
        'BO-Fam:MA-SF': 150}

    properties = [
        'PwrState-Sel', 'PwrState-Sts',
        'OpMode-Sel', 'OpMode-Sts',
        'CycleType-Sel', 'CycleType-Sts',
        'CycleFreq-SP', 'CycleFreq-RB',
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleOffset-SP', 'CycleOffset-RB',
        'CycleNrCycles-SP', 'CycleNrCycles-RB',
        'CycleAuxParam-SP', 'CycleAuxParam-RB',
        'CycleEnbl-Mon',
        'WfmData-SP', 'WfmData-RB',
        'RmpIncNrCycles-SP', 'RmpIncNrCycles-RB',
        'RmpReady-Mon',
        'Current-SP',
    ]

    _base_wfmdata = _generate_base_wfmdata()

    def __init__(self, maname, ramp_config=None):
        """Constructor."""
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self.siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
        self._ramp_config = ramp_config
        self._pvs = dict()
        for prop in MagnetCycler.properties:
            if prop not in self._pvs.keys():
                pvname = VACA_PREFIX + self._maname + ':' + prop
                self._pvs[prop] = _PV(pvname, connection_timeout=TIMEOUT)
                self._pvs[prop].get()
        self._waveform = self._get_waveform()  # needs self._pvs

    def _get_waveform(self):
        if self._ramp_config is None:
            # Uses a template wfmdata scaled to maximum magnet ps current
            w = MagnetCycler._base_wfmdata
            if self.maname in MagnetCycler.RAMP_AMPLITUDE:
                # bypass upper_limit if maname in dictionary
                amp = MagnetCycler.RAMP_AMPLITUDE[self.maname]
            else:
                amp = self._pvs['Current-SP'].upper_ctrl_limit
            wfmdata = amp * w
        else:
            # load waveform from config database
            errmsg = ('Creation of waveform from ramp config '
                      'not yet implemented')
            raise NotImplementedError(errmsg)
        return wfmdata

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    @property
    def connected(self):
        """Return connected state."""
        for prop in MagnetCycler.properties:
            if not self[prop].connected:
                return False
        return True

    def cycle_duration(self, mode):
        """Return the duration of the cycling in seconds."""
        if mode == 'Demag':
            return self.siggen.num_cycles/self.siggen.freq
        else:
            return (Timing.DEFAULT_RAMP_TOTDURATION)

    def set_on(self):
        """Turn magnet PS on."""
        return self.conn_put(self['PwrState-Sel'],
                             _PSConst.PwrStateSel.On)

    def set_params(self, mode):
        """Set params to cycle."""
        status = True
        if mode == 'Demag':
            status &= self.conn_put(self['CycleType-Sel'],
                                    self.siggen.type)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['CycleFreq-SP'],
                                    self.siggen.freq)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['CycleAmpl-SP'],
                                    self.siggen.amplitude)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['CycleOffset-SP'],
                                    self.siggen.offset)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['CycleAuxParam-SP'],
                                    self.siggen.aux_param)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['CycleNrCycles-SP'],
                                    self.siggen.num_cycles)
        else:
            status &= self.conn_put(self['WfmData-SP'], self._waveform)
            _time.sleep(SLEEP_CAPUT)
            status &= self.conn_put(self['RmpIncNrCycles-SP'], 1)
        return status

    def set_opmode(self, opmode):
        """Set magnet opmode to mode."""
        return self.conn_put(self['OpMode-Sel'], opmode)

    def config_cycle(self, mode):
        """Config magnet to cycling mode."""
        status = True

        status &= self.set_opmode(_PSConst.OpMode.SlowRef)
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_on()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_params(mode)
        _time.sleep(SLEEP_CAPUT)

        opmode = _PSConst.OpMode.Cycle if mode == 'Demag'\
            else _PSConst.OpMode.RmpWfm
        status &= self.set_opmode(opmode)
        return status

    def on_rdy(self):
        """Return wether magnet PS is on."""
        status = self.timed_get(
            self['PwrState-Sts'], _PSConst.PwrStateSts.On)
        return status

    def params_rdy(self, mode):
        """Return wether magnet cycling parameters are set."""
        status = True
        if mode == 'Demag':
            type_idx = _PSet.CYCLE_TYPES.index(self.siggen.type)
            status &= self.timed_get(self['CycleType-Sts'], type_idx)
            status &= self.timed_get(
                self['CycleFreq-RB'], self.siggen.freq)
            status &= self.timed_get(
                self['CycleAmpl-RB'], self.siggen.amplitude)
            status &= self.timed_get(
                self['CycleOffset-RB'], self.siggen.offset)
            status &= self.timed_get(
                self['CycleAuxParam-RB'], self.siggen.aux_param)
            status &= self.timed_get(
                self['CycleNrCycles-RB'], self.siggen.num_cycles)
        else:
            status &= self.timed_get(self['RmpIncNrCycles-RB'], 1)
            _time.sleep(SLEEP_CAPUT)
            status &= self.timed_get(
                self['WfmData-RB'], Timing.DEFAULT_RMPBO_NRPULSES*[0])
        return status

    def mode_rdy(self, mode):
        """Return wether magnet is in mode."""
        opmode = _PSConst.States.Cycle if mode == 'Demag'\
            else _PSConst.States.RmpWfm
        return self.timed_get(self['OpMode-Sts'], opmode)

    def is_ready(self, mode):
        """Return wether magnet is ready."""
        status = True
        status &= self.on_rdy()
        status &= self.params_rdy(mode)
        status &= self.mode_rdy(mode)
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
                elif len(value) != len(pvvalue):
                    status = False
                else:
                    for i in range(len(value)):
                        if _isclose(pvvalue[i], value[i],
                                    rel_tol=1e-06, abs_tol=0.0):
                            status = True
                            break
                        else:
                            status = False
                    else:
                        break
            else:
                if _isclose(pvvalue, value, rel_tol=1e-06, abs_tol=0.0):
                    status = True
                    break
                else:
                    status = False
            _time.sleep(wait/10.0)
        return status

    def __getitem__(self, prop):
        """Return item."""
        return self._pvs[prop]
