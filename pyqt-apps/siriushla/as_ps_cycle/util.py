"""Utilities for ps-cycle."""

import sys as _sys
import re as _re
import time as _time
import logging as _log
from epics import PV as _PV
from math import isclose as _isclose
import numpy as _np

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.timesys import Const as _TIConst
from siriuspy.csdevice.pwrsupply import ETypes as _PSet
from siriuspy.namesys import Filter as _Filter
from siriushla.as_ps_cycle.ramp_data import BASE_RAMP_CURVE_ORIG as \
    _BASE_RAMP_CURVE_ORIG


TIMEOUT = 0.05
SLEEP_CAPUT = 0.1


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
    DEFAULT_RAMP_NRPULSES = 4000
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
            'RA-RaMO:TI-EVG:InjectionEvt-Sts': _TIConst.DsblEnbl.Dsbl,
            'RA-RaMO:TI-EVG:BucketList-SP': [1, ],
            'RA-RaMO:TI-EVG:RepeatBucketList-SP': DEFAULT_RAMP_NRCYCLES,
            'RA-RaMO:TI-EVG:InjCount-Mon': None,

            # Cycle event settings
            'RA-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.Injection,
            'RA-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Incr,
            'RA-RaMO:TI-EVG:CycleDelay-SP': DEFAULT_DELAY,
        }
    }

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

    _pvs = None

    def __init__(self):
        """Init."""
        self._create_pvs()
        self._status_nok = []

    @property
    def status_nok(self):
        """Return list with names of failing PVs."""
        return self._status_nok.copy()

    def init(self, mode, sections=list()):
        """Initialize properties."""
        filt = self._create_section_re(sections)
        for prop, defval in Timing.properties[mode].items():
            if 'RA-RaMO:TI-EVG' not in prop and not filt.search(prop):
                continue
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

    def trigger(self, mode):
        """Trigger timming to cycle magnets."""
        if mode == 'Cycle':
            pv = Timing._pvs['RA-RaMO:TI-EVG:CycleExtTrig-Cmd']
            pv.value = 1
        else:
            pv = Timing._pvs['RA-RaMO:TI-EVG:InjectionEvt-Sel']
            pv.value = _TIConst.DsblEnbl.Enbl
            # Wait for timing to turn injection mode on
            _time.sleep(50*SLEEP_CAPUT)

    def wait_trigger_enable(self, mode):
        # Wait for timing to turn injection mode on
        if mode == 'Ramp':
            pv_sts = Timing._pvs['RA-RaMO:TI-EVG:InjectionEvt-Sts']
            while pv_sts.value != _TIConst.DsblEnbl.Enbl:
                _time.sleep(TIMEOUT)

    def get_cycle_count(self):
        pv = Timing._pvs['RA-RaMO:TI-EVG:InjCount-Mon']
        return pv.value

    def check_ramp_end(self):
        pv = Timing._pvs['RA-RaMO:TI-EVG:InjCount-Mon']
        return (pv.value == Timing.DEFAULT_RAMP_NRCYCLES)

    def reset(self):
        pv_event = Timing._pvs['RA-RaMO:TI-EVG:CycleMode-Sel']
        pv_event.value = _TIConst.EvtModes.Disabled
        pv_bktlist = Timing._pvs['RA-RaMO:TI-EVG:RepeatBucketList-SP']
        pv_bktlist.value = 0
        for trig in self._trigger_list:
            pv = Timing._pvs[trig+':Src-Sel']
            pv.value = 'Dsbl'

    def _create_pvs(self):
        """Create PVs."""
        Timing._pvs = dict()
        for mode, dict_ in Timing.properties.items():
            for pvname in dict_.keys():
                Timing._pvs[pvname] = _PV(VACA_PREFIX+pvname,
                                          connection_timeout=TIMEOUT)
                Timing._pvs[pvname].get()

    @staticmethod
    def _create_section_re(sections):
        filt = ''
        for sec in sections:
            if filt != '':
                filt += '|'
            filt += sec+'-'
        return _re.compile(filt)


class MagnetCycler:
    """Handle magnet properties related to Cycle and RmpWfm ps modes."""

    RAMP_AMPLITUDE = {  # A
        'BO-Fam:MA-B':  1072,
        'BO-Fam:MA-QD': 30,
        'BO-Fam:MA-QF': 120,
        'BO-Fam:MA-SD': 149,
        'BO-Fam:MA-SF': 149}

    properties = [
        'Current-SP', 'Current-RB',
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
        'PRUSyncPulseCount-Mon',
        'IntlkSoft-Mon', 'IntlkHard-Mon'
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
        if mode == 'Cycle':
            return self.siggen.num_cycles/self.siggen.freq
        else:
            return (Timing.DEFAULT_RAMP_TOTDURATION)

    def set_on(self):
        """Turn magnet PS on."""
        return self.conn_put(self['PwrState-Sel'],
                             _PSConst.PwrStateSel.On)

    def set_current_2_zero(self):
        """Set PS current to zero ."""
        return self.conn_put(self['Current-SP'], 0)

    def set_params(self, mode):
        """Set params to cycle."""
        status = True
        if mode == 'Cycle':
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

    def config_cycle_params(self, mode):
        """Config magnet to cycling mode."""
        status = True

        status &= self.set_opmode(_PSConst.OpMode.SlowRef)
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_on()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_current_2_zero()
        _time.sleep(SLEEP_CAPUT)

        status &= self.set_params(mode)
        _time.sleep(5*SLEEP_CAPUT)
        return status

    def config_cycle_opmode(self, mode):
        opmode = _PSConst.OpMode.Cycle if mode == 'Cycle'\
            else _PSConst.OpMode.RmpWfm
        return self.set_opmode(opmode)

    def on_rdy(self):
        """Return wether magnet PS is on."""
        return self.timed_get(self['PwrState-Sts'], _PSConst.PwrStateSts.On)

    def current_rdy(self):
        """Return wether magnet PS current is zero."""
        return self.timed_get(self['Current-RB'], 0)

    def params_rdy(self, mode):
        """Return wether magnet cycling parameters are set."""
        status = True
        if mode == 'Cycle':
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
            status &= self.timed_get(self['WfmData-RB'], self._waveform)
            _time.sleep(SLEEP_CAPUT)
            status &= self.timed_get(self['RmpIncNrCycles-RB'], 1)
        return status

    def mode_rdy(self, mode):
        """Return wether magnet is in mode."""
        opmode = _PSConst.States.Cycle if mode == 'Cycle'\
            else _PSConst.States.RmpWfm
        return self.timed_get(self['OpMode-Sts'], opmode)

    def is_ready(self, mode):
        """Return wether magnet is ready."""
        status = True
        status &= self.on_rdy()
        status &= self.current_rdy()
        status &= self.params_rdy(mode)
        status &= self.mode_rdy(mode)
        return status

    def check_cycle_enable(self):
        return self.timed_get(self['CycleEnbl-Mon'], _PSConst.DsblEnbl.Enbl)

    def check_final_state(self, mode):
        status = True
        status &= self.reset_opmode()
        _time.sleep(5*SLEEP_CAPUT)
        status &= self.timed_get(self['PwrState-Sts'], _PSConst.PwrStateSts.On)
        status &= self.timed_get(self['IntlkSoft-Mon'], 0)
        status &= self.timed_get(self['IntlkHard-Mon'], 0)
        if not status:
            return 2  # indicate interlock problems

        if mode == 'Ramp':
            pulses = Timing.DEFAULT_RAMP_NRCYCLES*Timing.DEFAULT_RAMP_NRPULSES
            status = self.timed_get(self['PRUSyncPulseCount-Mon'], pulses)
            return 1  # indicate lack of trigger pulses

        return 0

    def reset_opmode(self):
        return self.set_opmode(_PSConst.OpMode.SlowRef)

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


class AutomatedCycle:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=None, timing=None,
                 ramp_config=None, logger=None):
        """Initialize."""
        if cyclers:
            self.cyclers = cyclers
        else:
            self.cyclers = dict()
            for maname in get_manames():
                self.cyclers[maname] = MagnetCycler(maname, ramp_config)
        self._timing = timing if timing is not None else Timing()

        self._logger = logger
        self._logger_message = ''
        _log.basicConfig(
            format='%(asctime)s %(levelname)8s %(name)s | %(message)s',
            datefmt='%F %T', level=_log.INFO, stream=_sys.stdout)

        self._cycle_duration = 0
        for ma in self.manames_2_cycle:
            self._cycle_duration = max(
                self._cycle_duration, self.cyclers[ma].cycle_duration('Cycle'))

        self._ramp_duration = 0
        for ma in self.manames_2_ramp:
            self._ramp_duration = max(
                self._ramp_duration, self.cyclers[ma].cycle_duration('Ramp'))

        self.aborted = False

    @property
    def manames_2_cycle(self):
        """Return manames to cycle."""
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'TB', 'dis': 'MA'})
        # TODO: uncomment when using TS and SI
        #    self.cyclers.keys(), filters={'sec': '(TB|TS|SI)', 'dis': 'MA'})

    @property
    def manames_2_ramp(self):
        """Return manames to ramp."""
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'BO', 'dis': 'MA'})

    def prepare_all_magnets(self, mode):
        """Prepare magnets to cycle according to mode."""
        manames = self.manames_2_cycle if mode == 'Cycle'\
            else self.manames_2_ramp
        # Set all magnets params
        for maname in manames:
            self._update_log('Preparing '+maname+' params...')
            self.cyclers[maname].config_cycle_params(mode)
            if self.aborted:
                self._update_log('Aborted.')
                return
            self._update_log(done=True)
        # Change all magnets OpMode
        for maname in manames:
            self._update_log('Preparing '+maname+' opmode...')
            self.cyclers[maname].config_cycle_opmode(mode)
            if self.aborted:
                self._update_log('Aborted.')
                return
            self._update_log(done=True)

    def prepare_timing(self, mode):
        """Prepare timing to cycle according to mode."""
        sections = ['TB', ] if mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Preparing Timing...')
        self._timing.init(mode, sections)
        self._update_log(done=True)

    def check_magnets_preparation(self, mode):
        manames = self.manames_2_cycle if mode == 'Cycle'\
            else self.manames_2_ramp
        # Check all magnets params
        for maname in manames:
            self._update_log('Checking '+maname+' settings...')
            is_ready = self.cyclers[maname].is_ready(mode)
            if self.aborted:
                self._update_log('Aborted.')
                return False
            if is_ready:
                self._update_log(done=True)
            else:
                self._update_log(maname+' is not ready.')
                return False
        return True

    def check_magnets_final_state(self, mode):
        manames = self.manames_2_cycle if mode == 'Cycle'\
            else self.manames_2_ramp
        # Check all magnets params
        for maname in manames:
            self._update_log('Checking '+maname+' final state...')
            has_prob = self.cyclers[maname].check_final_state(mode)
            if self.aborted:
                self._update_log('Aborted.')
                return False
            if not has_prob:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(maname+' is not ok after '+mode.lower())
            else:
                self._update_log(maname+' has interlock problems.')
        return True

    def init(self, mode):
        """Trigger timing according to mode to init cycling."""
        self._update_log('Triggering timing...')
        self._timing.trigger(mode)
        self._update_log(done=True)

    def wait(self, mode):
        """Wait/Sleep while cycling according to mode."""
        self._update_log('Waiting for cycling...')
        t0 = _time.time()
        keep_waiting = True
        while keep_waiting:
            _time.sleep(1)
            if mode == 'Cycle':
                t = round(self._cycle_duration - (_time.time()-t0))
            else:
                t = round(self._ramp_duration -
                          self._timing.get_cycle_count() *
                          self._timing.DEFAULT_RAMP_DURATION/1000000)
            self._update_log('Remaining time: {}s...'.format(t))
            if (mode == 'Cycle') and (2 < _time.time() - t0 < 5):
                maname = self.manames_2_cycle[0]
                status = self.cyclers[maname].check_cycle_enable()
                if not status:
                    self._update_log(
                        'Magnets are not cycling! Verify triggers!')
                    return False
            if mode == 'Cycle':
                keep_waiting = _time.time() - t0 < self._cycle_duration
            else:
                keep_waiting = not self._timing.check_ramp_end()
        self._update_log(done=True)
        return True

    def reset_all_subsystems(self):
        self._update_log('Turning TI off and setting magnets to SlowRef...')
        _time.sleep(4)
        for ma in self.manames_2_cycle:
            self.cyclers[ma].reset_opmode()
        for ma in self.manames_2_ramp:
            self.cyclers[ma].reset_opmode()
        self._timing.reset()
        self._update_log(done=True)

    def execute(self):
        """Execute automated cycle."""
        # Cycle
        if self.manames_2_cycle:
            self.prepare_all_magnets('Cycle')
            if self.aborted:
                return
            self.prepare_timing('Cycle')
            if self.aborted:
                return
            self._update_log('Waiting to check magnets state...')
            _time.sleep(10)
            status = self.check_magnets_preparation('Cycle')
            if not status:
                _log.warning('There are magnets not ready to cycle.')
                return
            if self.aborted:
                return
            self.init('Cycle')
            status = self.wait('Cycle')
            if not status:
                return
            self.check_magnets_final_state('Cycle')

        # Ramp
        if self.manames_2_ramp:
            self.prepare_all_magnets('Ramp')
            if self.aborted:
                return
            self.prepare_timing('Ramp')
            if self.aborted:
                return
            self._update_log('Waiting to check magnets state...')
            _time.sleep(10)
            status = self.check_magnets_preparation('Ramp')
            if not status:
                _log.warning('There are magnets not ready to ramp.')
                return
            if self.aborted:
                return
            self.init('Ramp')
            self.wait('Ramp')
            self.check_magnets_final_state('Ramp')

        self.reset_all_subsystems()

        # Indicate cycle end
        self._update_log('Cycle finished sucessfully!')

    def _update_log(self, message='', done=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done)
        if done and not message:
            message = 'Done.'
        _log.info(message)
