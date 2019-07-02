"""Utilities for ps-cycle."""

import sys as _sys
import time as _time
import logging as _log
import threading as _thread
from epics import PV as _PV
from math import isclose as _isclose
import numpy as _np

from siriuspy.namesys import SiriusPVName as _SiriusPVName, \
    get_pair_sprb as _get_pair_sprb, Filter as _Filter
from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst, ETypes as _PSet
from siriuspy.csdevice.timesys import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db
from siriushla.as_ps_cycle.ramp_data import BASE_RAMP_CURVE_ORIG as \
    _BASE_RAMP_CURVE_ORIG


TIMEOUT_CONNECTION = 0.05
SLEEP_CAPUT = 0.1
TIMEOUT_CHECK = 20


def get_manames():
    """Return manames."""
    return _MASearch.get_manames({'sec': '(TB|BO)', 'dis': 'MA'})
    # TODO: uncomment when using TS and SI
    # return _MASearch.get_manames({'sec': '(TB|BO|TS|SI)', 'dis': 'MA'})


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
    nrpulses = Timing.DEFAULT_RAMP_NRPULSES
    duration = Timing.DEFAULT_RAMP_DURATION/1000.0
    t = _np.linspace(0.0, duration, nrpulses)
    w = _np.interp(t, t0, w0)
    return w


class Timing:
    """Timing."""

    EVTNAME_CYCLE = 'Cycle'

    DEFAULT_CYCLE_DURATION = 150  # [us]
    DEFAULT_CYCLE_NRPULSES = 1
    DEFAULT_RAMP_DURATION = 490000  # [us]
    DEFAULT_RAMP_NRPULSES = 3920
    DEFAULT_DELAY = 0  # [us]
    DEFAULT_POLARITY = _TIConst.TrigPol.Normal  # test
    DEFAULT_STATE = _TIConst.DsblEnbl.Enbl

    DEFAULT_RAMP_NRCYCLES = 16
    DEFAULT_RAMP_TOTDURATION = DEFAULT_RAMP_DURATION * \
        DEFAULT_RAMP_NRCYCLES/1000000  # [s]

    _trigger_list = [
        'TB-Glob:TI-Mags', 'BO-Glob:TI-Mags', 'BO-Glob:TI-Corrs']
    # TODO: uncomment when using TS and SI
    #    'TS-Glob:TI-Mags', 'SI-Glob:TI-Dips', 'SI-Glob:TI-Quads',
    #    'SI-Glob:TI-Sexts', 'SI-Glob:TI-Skews', 'SI-Glob:TI-Corrs']

    properties = {
        'Cycle': {
            # EVG settings
            'RA-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'RA-RaMO:TI-EVG:UpdateEvt-Cmd': 1,

            # Cycle event settings
            'RA-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.External,
            'RA-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Fixed,
            'RA-RaMO:TI-EVG:CycleExtTrig-Cmd': None,
        },
        'Ramp': {
            # EVG settings
            'RA-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'RA-RaMO:TI-EVG:InjectionEvt-Sel': _TIConst.DsblEnbl.Dsbl,
            'RA-RaMO:TI-EVG:BucketList-SP': [1, ],
            'RA-RaMO:TI-EVG:RepeatBucketList-SP': DEFAULT_RAMP_NRCYCLES,
            'RA-RaMO:TI-EVG:InjCount-Mon': None,

            # Cycle event settings
            'RA-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.Injection,
            'RA-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Incr,
            'RA-RaMO:TI-EVG:CycleDelay-SP': DEFAULT_DELAY,
        }
    }

    cycle_idx = dict()
    for trig in _trigger_list:
        properties['Cycle'][trig+':Src-Sel'] = EVTNAME_CYCLE
        properties['Cycle'][trig+':Duration-SP'] = DEFAULT_CYCLE_DURATION
        properties['Cycle'][trig+':NrPulses-SP'] = DEFAULT_CYCLE_NRPULSES
        properties['Cycle'][trig+':Delay-SP'] = DEFAULT_DELAY
        properties['Cycle'][trig+':Polarity-Sel'] = DEFAULT_POLARITY
        properties['Cycle'][trig+':State-Sel'] = DEFAULT_STATE

        properties['Ramp'][trig+':Src-Sel'] = EVTNAME_CYCLE
        properties['Ramp'][trig+':Duration-SP'] = DEFAULT_RAMP_DURATION
        properties['Ramp'][trig+':NrPulses-SP'] = DEFAULT_RAMP_NRPULSES
        properties['Ramp'][trig+':Delay-SP'] = DEFAULT_DELAY
        properties['Ramp'][trig+':Polarity-Sel'] = DEFAULT_POLARITY
        properties['Ramp'][trig+':State-Sel'] = DEFAULT_STATE

        _trig_db = _get_trig_db(trig)
        cycle_idx[trig] = _trig_db['Src-Sel']['enums'].index('Cycle')

    _pvs = dict()

    def __init__(self):
        """Init."""
        self._initial_state = dict()
        self._create_pvs()

    def connected(self, sections=list(), return_disconn=False):
        """Return connected state."""
        disconn = set()
        for name, pv in Timing._pvs.items():
            if sections and _SiriusPVName(name).sec not in sections:
                continue
            if not pv.connected:
                disconn.add(pv.pvname)
        if return_disconn:
            return disconn
        return not bool(disconn)

    def get_pvnames_by_section(self, sections=list()):
        pvnames = set()
        for mode in Timing.properties.keys():
            for prop in Timing.properties[mode].keys():
                prop = _SiriusPVName(prop)
                if prop.dev == 'EVG' or prop.sec in sections:
                    pvnames.add(prop)
        return pvnames

    def get_pvname_2_defval_dict(self, mode, sections=list()):
        pvname_2_defval_dict = dict()
        for prop, defval in Timing.properties[mode].items():
            if defval is None:
                continue
            prop = _SiriusPVName(prop)
            if prop.dev == 'EVG' or prop.sec in sections:
                pvname_2_defval_dict[prop] = defval
        return pvname_2_defval_dict

    def prepare(self, mode, sections=list()):
        """Initialize properties."""
        pvs_2_init = self.get_pvname_2_defval_dict(mode, sections)
        for prop, defval in pvs_2_init.items():
            pv = Timing._pvs[prop]
            pv.get()  # force connection
            if pv.connected:
                pv.value = defval
                _time.sleep(1.5*SLEEP_CAPUT)

    def check(self, mode, sections=list()):
        """Check if timing is configured."""
        pvs_2_init = self.get_pvname_2_defval_dict(mode, sections)
        for prop, defval in pvs_2_init.items():
            try:
                prop_sts = _get_pair_sprb(prop)[1]
            except TypeError:
                continue
            pv = Timing._pvs[prop_sts]
            pv.get()  # force connection
            if not pv.connected:
                return False
            else:
                if prop_sts.propty_name == 'Src':
                    defval = Timing.cycle_idx[prop_sts.device_name]

                if prop_sts.propty_name.endswith(('Duration', 'Delay')):
                    tol = 0.008 * 1.5
                    if mode == 'Ramp':
                        tol *= self.DEFAULT_RAMP_NRPULSES
                    if not _isclose(pv.value, defval, abs_tol=tol):
                        return False
                elif isinstance(defval, (_np.ndarray, list, tuple)):
                    if _np.any(pv.value[0:len(defval)] != defval):
                        return False
                elif pv.value != defval:
                    return False
        return True

    def trigger(self, mode):
        """Trigger timming to cycle magnets."""
        if mode == 'Cycle':
            pv = Timing._pvs['RA-RaMO:TI-EVG:CycleExtTrig-Cmd']
            pv.value = 1
        else:
            pv = Timing._pvs['RA-RaMO:TI-EVG:InjectionEvt-Sel']
            pv.value = _TIConst.DsblEnbl.Enbl

            pv = Timing._pvs['RA-RaMO:TI-EVG:InjectionEvt-Sts']
            t0 = _time.time()
            while _time.time() - t0 < TIMEOUT_CHECK:
                if pv.value == _TIConst.DsblEnbl.Enbl:
                    break
                _time.sleep(SLEEP_CAPUT)

    def get_cycle_count(self):
        pv = Timing._pvs['RA-RaMO:TI-EVG:InjCount-Mon']
        return pv.value

    def check_ramp_end(self):
        pv = Timing._pvs['RA-RaMO:TI-EVG:InjCount-Mon']
        return (pv.value == Timing.DEFAULT_RAMP_NRCYCLES)

    def turnoff(self):
        """Turn timing off."""
        pv_event = Timing._pvs['RA-RaMO:TI-EVG:CycleMode-Sel']
        pv_event.value = _TIConst.EvtModes.Disabled
        pv_bktlist = Timing._pvs['RA-RaMO:TI-EVG:RepeatBucketList-SP']
        pv_bktlist.value = 0
        for trig in self._trigger_list:
            pv = Timing._pvs[trig+':Src-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl
            pv = Timing._pvs[trig+':State-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl

    def restore_initial_state(self):
        """Restore initial state."""
        for pvname, init_val in self._initial_state.items():
            if ':BucketList-SP' in pvname and isinstance(init_val, int):
                init_val = [init_val, ]
            Timing._pvs[pvname].put(init_val)
            _time.sleep(1.5*SLEEP_CAPUT)

    def _create_pvs(self):
        """Create PVs."""
        Timing._pvs = dict()
        for mode, dict_ in Timing.properties.items():
            for pvname in dict_.keys():
                if pvname in Timing._pvs.keys():
                    continue
                pvname = _SiriusPVName(pvname)
                Timing._pvs[pvname] = _PV(
                    VACA_PREFIX+pvname, connection_timeout=TIMEOUT_CONNECTION)
                self._initial_state[pvname] = Timing._pvs[pvname].get()

                if pvname.propty_suffix == 'SP':
                    pvname_sts = pvname.substitute(propty_suffix='RB')
                elif pvname.propty_suffix == 'Sel':
                    pvname_sts = pvname.substitute(propty_suffix='Sts')
                else:
                    continue
                Timing._pvs[pvname_sts] = _PV(
                    VACA_PREFIX+pvname_sts,
                    connection_timeout=TIMEOUT_CONNECTION)
                Timing._pvs[pvname_sts].get()  # force connection


class MagnetCycler:
    """Handle magnet properties related to Cycle and RmpWfm ps modes."""

    RAMP_AMPLITUDE = {  # A
        'BO-Fam:MA-B':  1072,
        'BO-Fam:MA-QD': 30,
        'BO-Fam:MA-QF': 120,
        'BO-Fam:MA-SD': 149,
        'BO-Fam:MA-SF': 149}

    properties = [
        'Current-SP', 'Current-RB', 'CurrentRef-Mon',
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
        'PRUSyncPulseCount-Mon',
        'IntlkSoft-Mon', 'IntlkHard-Mon'
    ]

    _base_wfmdata = _generate_base_wfmdata()

    def __init__(self, maname, ramp_config=None):
        """Constructor."""
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._siggen = None
        self._ramp_config = ramp_config
        self._waveform = None
        self._pvs = dict()
        for prop in MagnetCycler.properties:
            if prop not in self._pvs.keys():
                pvname = VACA_PREFIX + self._maname + ':' + prop
                self._pvs[prop] = _PV(
                    pvname, connection_timeout=TIMEOUT_CONNECTION)
                self._pvs[prop].get()

    def _get_waveform(self):
        if self._ramp_config is None:
            # Uses a template wfmdata scaled to maximum magnet ps current
            w = MagnetCycler._base_wfmdata
            if self.maname in MagnetCycler.RAMP_AMPLITUDE:
                # bypass upper_limit if maname in dictionary
                amp = MagnetCycler.RAMP_AMPLITUDE[self.maname]
            else:
                amp = _MASearch.get_splims(self.maname, 'hilim')
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

    @property
    def waveform(self):
        if self._waveform is None:
            self._waveform = self._get_waveform()  # needs self._pvs
        return self._waveform

    @property
    def siggen(self):
        if self._siggen is None:
            self._siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
        return self._siggen

    def cycle_duration(self, mode):
        """Return the duration of the cycling in seconds."""
        if mode == 'Cycle':
            return self.siggen.num_cycles/self.siggen.freq
        else:
            return (Timing.DEFAULT_RAMP_TOTDURATION)

    def check_intlks(self):
        status = self._timed_get(self['IntlkSoft-Mon'], 0)
        status &= self._timed_get(self['IntlkHard-Mon'], 0)
        return status

    def check_on(self):
        """Return wether magnet PS is on."""
        return self._timed_get(self['PwrState-Sts'], _PSConst.PwrStateSts.On)

    def set_current_zero(self):
        """Set PS current to zero ."""
        return self._conn_put(self['Current-SP'], 0)

    def check_current_zero(self):
        """Return wether magnet PS current is zero."""
        return self._timed_get(self['CurrentRef-Mon'], 0)

    def set_params(self, mode):
        """Set params to cycle."""
        status = True
        if mode == 'Cycle':
            status &= self._conn_put(self['CycleType-Sel'],
                                     self.siggen.type)
            _time.sleep(SLEEP_CAPUT)
            status &= self._conn_put(self['CycleFreq-SP'],
                                     self.siggen.freq)
            _time.sleep(SLEEP_CAPUT)
            status &= self._conn_put(self['CycleAmpl-SP'],
                                     self.siggen.amplitude)
            _time.sleep(SLEEP_CAPUT)
            status &= self._conn_put(self['CycleOffset-SP'],
                                     self.siggen.offset)
            _time.sleep(SLEEP_CAPUT)
            status &= self._conn_put(self['CycleAuxParam-SP'],
                                     self.siggen.aux_param)
            _time.sleep(SLEEP_CAPUT)
            status &= self._conn_put(self['CycleNrCycles-SP'],
                                     self.siggen.num_cycles)
        else:
            status &= self._conn_put(self['WfmData-SP'], self.waveform)
        return status

    def check_params(self, mode):
        """Return wether magnet cycling parameters are set."""
        status = True
        if mode == 'Cycle':
            type_idx = _PSet.CYCLE_TYPES.index(self.siggen.type)
            status &= self._timed_get(self['CycleType-Sts'], type_idx)
            status &= self._timed_get(
                self['CycleFreq-RB'], self.siggen.freq)
            status &= self._timed_get(
                self['CycleAmpl-RB'], self.siggen.amplitude)
            status &= self._timed_get(
                self['CycleOffset-RB'], self.siggen.offset)
            status &= self._timed_get(
                self['CycleAuxParam-RB'], self.siggen.aux_param)
            status &= self._timed_get(
                self['CycleNrCycles-RB'], self.siggen.num_cycles)
        else:
            status &= self._timed_get(self['WfmData-RB'], self.waveform)
        return status

    def prepare(self, mode):
        """Config magnet to cycling mode."""
        status = True

        status &= self.set_opmode_slowref()
        status &= self._timed_get(self['OpMode-Sts'], _PSConst.States.SlowRef)

        status &= self.set_current_zero()
        status &= self.check_current_zero()

        status &= self.set_params(mode)
        status &= self.check_params(mode)
        return status

    def is_prepared(self, mode):
        """Return wether magnet is ready."""
        status = True
        status &= self.check_current_zero()
        status &= self.check_params(mode)
        return status

    def set_opmode(self, opmode):
        """Set magnet opmode to mode."""
        return self._conn_put(self['OpMode-Sel'], opmode)

    def set_opmode_slowref(self):
        return self.set_opmode(_PSConst.OpMode.SlowRef)

    def set_opmode_cycle(self, mode):
        opmode = _PSConst.OpMode.Cycle if mode == 'Cycle'\
            else _PSConst.OpMode.RmpWfm
        return self.set_opmode(opmode)

    def check_opmode_cycle(self, mode):
        """Return wether magnet is in mode."""
        opmode = _PSConst.States.Cycle if mode == 'Cycle'\
            else _PSConst.States.RmpWfm
        return self._timed_get(self['OpMode-Sts'], opmode)

    def get_cycle_enable(self):
        return self._timed_get(self['CycleEnbl-Mon'], _PSConst.DsblEnbl.Enbl)

    def check_final_state(self, mode):
        if mode == 'Ramp':
            pulses = Timing.DEFAULT_RAMP_NRCYCLES*Timing.DEFAULT_RAMP_NRPULSES
            status = self._timed_get(
                self['PRUSyncPulseCount-Mon'], pulses, wait=10.0)
            if not status:
                return 1  # indicate lack of trigger pulses
            status = self.set_opmode_slowref()
            status &= self._timed_get(
                self['OpMode-Sts'], _PSConst.States.SlowRef)
        else:
            status = self._timed_get(
                self['OpMode-Sts'], _PSConst.States.SlowRef, wait=10.0)
            if not status:
                return 2  # indicate cycling not finished yet

        status &= self._timed_get(self['PwrState-Sts'],
                                  _PSConst.PwrStateSts.On)
        status &= self._timed_get(self['IntlkSoft-Mon'], 0, wait=1.0)
        status &= self._timed_get(self['IntlkHard-Mon'], 0, wait=1.0)
        if not status:
            return 3  # indicate interlock problems

        return 0

    def _conn_put(self, pv, value):
        """Put if connected."""
        if not pv.connected:
            return False
        if pv.put(value):
            return True
        return False

    def _timed_get(self, pv, value, wait=50*SLEEP_CAPUT):
        """Do timed get."""
        if not pv.connected:
            return False
        t0 = _time.time()
        while _time.time() - t0 < wait:
            pvvalue = pv.get()
            status = False
            if isinstance(value, (tuple, list, _np.ndarray)):
                if not isinstance(pvvalue, (tuple, list, _np.ndarray)):
                    status = False
                elif len(value) != len(pvvalue):
                    status = False
                else:
                    for i in range(len(value)):
                        if _isclose(pvvalue[i], value[i],
                                    rel_tol=1e-06, abs_tol=0.0):
                            status = True
                        else:
                            status = False
                            break
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


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=None, timing=None,
                 is_bo=False, ramp_config=None, logger=None):
        """Initialize."""
        if cyclers:
            self.cyclers = cyclers
        else:
            if is_bo:
                manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})
            else:
                manames = _MASearch.get_manames({'sec': 'TB', 'dis': 'MA'})
                # manames = _MASearch.get_manames(
                #     {'sec': '(TB|TS|SI)', 'dis': 'MA'})
            self.cyclers = dict()
            for maname in manames:
                self.cyclers[maname] = MagnetCycler(maname, ramp_config)
        self._timing = timing if timing is not None else Timing()

        self._logger = logger
        self._logger_message = ''
        if not logger:
            _log.basicConfig(
                format='%(asctime)s | %(message)s',
                datefmt='%F %T', level=_log.INFO, stream=_sys.stdout)

        ma2cycle = self._manames_2_cycle()
        ma2ramp = self._manames_2_ramp()
        if ma2cycle and ma2ramp:
            raise Exception('Can not cycle Booster with other accelerators!')
        elif ma2cycle:
            self._mode = 'Cycle'
        else:
            self._mode = 'Ramp'

        self._cycle_duration = 0
        for ma in self.manames:
            self._cycle_duration = max(
                self._cycle_duration,
                self.cyclers[ma].cycle_duration(self._mode))

        self.aborted = False
        self._prepare_size = None
        self._cycle_size = None

    @property
    def manames(self):
        """Magnets to cycle."""
        return self.cyclers.keys()

    @property
    def mode(self):
        """Mode."""
        return self._mode

    @property
    def prepare_size(self):
        """Prepare size."""
        if not self._prepare_size:
            s_check = len(self.manames) + 3
            s_prep = len(self.manames) + 3
            self._prepare_size = s_check + s_prep
        return self._prepare_size

    @property
    def cycle_size(self):
        """Cycle size."""
        if not self._cycle_size:
            s_check = len(self.manames)+3
            s_cycle = round(self._cycle_duration)+3*len(self.manames)+4
            self._cycle_size = s_check + s_cycle
        return self._cycle_size

    def prepare_all_magnets(self, ppty):
        """Prepare magnets to cycle according to mode."""
        threads = list()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.prepare_magnet, args=(maname, ppty), daemon=True)
            self._update_log('Preparing '+maname+' '+ppty+'...')
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

    def prepare_magnet(self, maname, ppty):
        """Prepare magnet parameters."""
        if ppty == 'parameters':
            self.cyclers[maname].prepare(self.mode)
        elif ppty == 'opmode':
            self.cyclers[maname].set_opmode_cycle(self.mode)

    def prepare_timing(self):
        """Prepare timing to cycle according to mode."""
        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Preparing Timing...')
        self._timing.prepare(self.mode, sections)
        self._update_log(done=True)

    def check_all_magnets(self, ppty):
        """Check all magnets according to mode."""
        threads = list()
        self._checks_result = dict()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.check_magnet,
                args=(maname, ppty), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return False

        for maname in self.manames:
            self._update_log('Checking '+maname+' '+ppty+'...')
            if self._checks_result[maname]:
                self._update_log(done=True)
            else:
                self._update_log(maname+' is not ready.', error=True)
                return False
        return True

    def check_magnet(self, maname, ppty):
        """Check magnet."""
        t0 = _time.time()
        cycler = self.cyclers[maname]
        r = False
        while _time.time()-t0 < TIMEOUT_CHECK:
            if ppty == 'parameters':
                r = cycler.is_prepared(self.mode)
            elif ppty == 'opmode':
                r = cycler.check_opmode_cycle(self.mode)
            if r:
                break
            _time.sleep(SLEEP_CAPUT)
        self._checks_result[maname] = r

    def check_timing(self):
        """Check timing preparation."""
        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Checking Timing...')
        t0 = _time.time()
        while _time.time()-t0 < TIMEOUT_CHECK:
            status = self._timing.check(self.mode, sections)
            if status:
                break
            _time.sleep(SLEEP_CAPUT)
        if not status:
            self._update_log('Timing is not configured.', error=True)
            return False
        else:
            self._update_log(done=True)
            return True

    def init(self):
        """Trigger timing according to mode to init cycling."""
        self._update_log('Triggering timing...')
        self._timing.trigger(self.mode)
        self._update_log(done=True)

    def wait(self):
        """Wait/Sleep while cycling according to mode."""
        self._update_log('Waiting for cycling...')
        t0 = _time.time()
        keep_waiting = True
        while keep_waiting:
            _time.sleep(1)
            if self.mode == 'Cycle':
                t = round(self._cycle_duration - (_time.time()-t0))
            else:
                t = round(self._cycle_duration -
                          self._timing.get_cycle_count() *
                          self._timing.DEFAULT_RAMP_DURATION/1000000)
            self._update_log('Remaining time: {}s...'.format(t))
            if (self.mode == 'Cycle') and (5 < _time.time() - t0 < 8):
                for maname in self.manames:
                    if not self.cyclers[maname].get_cycle_enable():
                        self._update_log(
                            'Magnets are not cycling! Verify triggers!',
                            error=True)
                        return False
            if self.mode == 'Cycle':
                keep_waiting = _time.time() - t0 < self._cycle_duration
            else:
                keep_waiting = not self._timing.check_ramp_end()
        self._update_log(done=True)
        return True

    def check_all_magnets_final_state(self):
        """Check all magnets final state according to mode."""
        threads = list()
        self._checks_final_result = dict()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.check_magnet_final_state,
                args=(maname, ), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return False

        for maname in self.manames:
            self._update_log('Checking '+maname+' final state...')
            has_prob = self._checks_final_result[maname]
            if not has_prob:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(
                    'Verify the number of pulses '+maname+' received!',
                    warning=True)
            elif has_prob == 2:
                self._update_log(maname+' is finishing cycling...',
                                 warning=True)
            else:
                self._update_log(maname+' has interlock problems.',
                                 error=True)
        return True

    def check_magnet_final_state(self, maname):
        """Check magnet final state."""
        self._checks_final_result[maname] = \
            self.cyclers[maname].check_final_state(self.mode)

    def reset_all_subsystems(self):
        """Reset all subsystems."""
        self._update_log('Setting magnets to SlowRef...')
        threads = list()
        for ma in self.manames:
            t = _thread.Thread(
                target=self.cyclers[ma].set_opmode_slowref, daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self._update_log('Restoring Timing initial state...')
        self._timing.restore_initial_state()
        self._update_log(done=True)

    # --- main commands ---

    def prepare(self):
        """Prepare to cycle."""
        self._timing.turnoff()

        self.prepare_all_magnets('parameters')
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return
        self.prepare_timing()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return
        if not self.check():
            return
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return
        self._update_log('Preparation finished!')

    def check(self):
        """Check cycle preparation."""
        if not self.check_all_magnets('parameters'):
            self._update_log(
                'There are magnets not configured to cycle. Stopping.',
                error=True)
            return False
        if not self.check_timing():
            return False
        return True

    def cycle(self):
        """Cycle."""
        if not self.check():
            return
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

        self.prepare_all_magnets('opmode')
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

        if not self.check_all_magnets('opmode'):
            self._update_log(
                'There are magnets with wrong opmode. Stopping.',
                error=True)
            return
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

        self.init()
        if not self.wait():
            return
        self.check_all_magnets_final_state()
        _time.sleep(4)
        self.reset_all_subsystems()

        # Indicate cycle end
        self._update_log('Cycle finished!')

    # --- private methods ---

    def _manames_2_cycle(self):
        """Return manames to cycle."""
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'TB', 'dis': 'MA'})
        # TODO: uncomment when using TS and SI
        #    self.cyclers.keys(), filters={'sec': '(TB|TS|SI)', 'dis': 'MA'})

    def _manames_2_ramp(self):
        """Return manames to ramp."""
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'BO', 'dis': 'MA'})

    def _update_log(self, message='', done=False, warning=False, error=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done, warning, error)
        else:
            if done and not message:
                message = 'Done.'
            _log.info(message)
