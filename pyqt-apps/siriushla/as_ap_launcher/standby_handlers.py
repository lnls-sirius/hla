import time as _time
from epics import PV as _PV

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch, HLTimeSearch, LLTimeSearch
from siriuspy.timesys.csdev import Const as TIConst, \
    get_hl_trigger_database as _get_trig_db
from siriuspy.pwrsupply.csdev import Const as PSConst

_BO_FAMS_TRIG_DB = _get_trig_db('BO-Glob:TI-Mags-Fams')
_BO_CORRS_TRIG_DB = _get_trig_db('BO-Glob:TI-Mags-Corrs')

TIMEOUT_WAIT = 3
EVG_NAME = LLTimeSearch.get_evg_name()
EVT_DSBL_VAL = TIConst.EvtModes.Disabled
EVT_CONT_VAL = TIConst.EvtModes.Continuous
TRG_ENBL_VAL = TIConst.DsblEnbl.Enbl
TRG_DSBL_VAL = TIConst.DsblEnbl.Dsbl
PU_ENBL_VAL = PSConst.DsblEnbl.Enbl
PU_DSBL_VAL = PSConst.DsblEnbl.Dsbl
PS_ENBL_VAL = PSConst.DsblEnbl.Enbl
PS_DSBL_VAL = PSConst.DsblEnbl.Dsbl
LILLRF_ENBL_VAL = PSConst.DsblEnbl.Enbl
LILLRF_DSBL_VAL = PSConst.DsblEnbl.Dsbl
PS_OPM_SLWREF = PSConst.OpMode.SlowRef
PS_STS_SLWREF = PSConst.States.SlowRef
PS_OPM_RMPWFM = PSConst.OpMode.RmpWfm
PS_STS_RMPWFM = PSConst.States.RmpWfm
BO_FAMS_EVT_INDEX = _BO_FAMS_TRIG_DB['Src-Sel']['enums'].index('RmpBO')
BO_CORRS_EVT_INDEX = _BO_CORRS_TRIG_DB['Src-Sel']['enums'].index('RmpBO')


class _BaseHandler:
    """Base Handler."""

    def _set_pvs(self, pvnames, value, wait=0):
        """Set PVs to value."""
        if isinstance(pvnames, str):
            pvnames = [pvnames, ]
        for pvname in pvnames:
            pv = self._pvs[pvname]
            if pv.wait_for_connection():
                pv.put(value)
                _time.sleep(wait)

    def _wait_pvs(self, pvnames, value):
        """Wait for PVs to reach value."""
        if isinstance(pvnames, str):
            pvnames = [pvnames, ]
        need_check = {pvn: True for pvn in pvnames}

        _time0 = _time.time()
        while any(need_check.values()):
            for pvn, tocheck in need_check.items():
                if not tocheck:
                    continue
                pv = self._pvs[pvn]
                need_check[pvn] = not pv.value == value
            _time.sleep(0.1)
            if _time.time() - _time0 > TIMEOUT_WAIT:
                break

        prob = list()
        for pvn, val in need_check.items():
            if val:
                try:
                    devname = str(_PVName(pvn).device_name)
                    if devname != EVG_NAME:
                        prob.append(devname)
                    else:
                        prob.append(str(pvn))
                except Exception:
                    prob.append(str(pvn))
        allok = not prob
        return allok, prob


class LILLRFStandbyHandler(_BaseHandler):
    """Linac LLRF Standby Mode Handler."""

    DEVICES = ('LA-RF:LLRF:BUN1',
               'LA-RF:LLRF:KLY1',
               'LA-RF:LLRF:KLY2')

    def __init__(self):
        """Init."""
        self._ppties = ('SET_INTEGRAL_ENABLE', 'GET_INTEGRAL_ENABLE',
                        'SET_FB_MODE', 'GET_FB_MODE')
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()
        for dev in self.DEVICES:
            for ppty in self._ppties:
                pvname = dev + ':' + ppty
                _pvs[pvname] = _PV(
                    _vaca_prefix+pvname, connection_timeout=0.05)
        self._pvs.update(_pvs)

    def turn_off(self):
        # turn feedback off
        pvs2set = [dev+':SET_FB_MODE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_DSBL_VAL)

        # wait for feedback to turn off
        pvs2wait = [dev+':GET_FB_MODE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_DSBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Feedback Mode to be off\n'\
                   'timed out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        # turn integral off
        pvs2set = [dev+':SET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_DSBL_VAL)

        # wait for integral to turn off
        pvs2wait = [dev+':GET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_DSBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Integral Mode to be off\n'\
                   'timed out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        return True, '', []

    def turn_on(self):
        # turn integral on
        pvs2set = [dev+':SET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_ENBL_VAL)

        # wait for integral to turn on
        pvs2wait = [dev+':GET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_ENBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Integral Mode to be on\n'\
                   'timed out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        # turn feedback on
        pvs2set = [dev+':SET_FB_MODE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_ENBL_VAL)

        # wait for feedback to turn on
        pvs2wait = [dev+':GET_FB_MODE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_ENBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Feedback Mode to be on\n'\
                   'timed out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        return True, '', []


class BOPSRampStandbyHandler(_BaseHandler):
    """Booster PS Ramp Standby Mode Handler."""

    DEVICES = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})
    TRIGGERS = HLTimeSearch.get_hl_triggers({'sec': 'BO', 'dev': 'Mags'})

    def __init__(self):
        """Init."""
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()
        pspropties = ['OpMode-Sel', 'OpMode-Sts', 'Current-SP', 'Current-RB',
                      'WfmUpdateAuto-Sel', 'WfmUpdateAuto-Sts']
        for psn in self.DEVICES:
            for propty in pspropties:
                pvn = psn+':'+propty
                _pvs[pvn] = _PV(_vaca_prefix+pvn, connection_timeout=0.05)

        tipropties = ['Src-Sel', 'Src-Sts', 'State-Sel', 'State-Sts']
        for trg in self.TRIGGERS:
            for propty in tipropties:
                pvn = trg+':'+propty
                _pvs[pvn] = _PV(_vaca_prefix+pvn, connection_timeout=0.05)

        self._pvs.update(_pvs)

    def turn_off(self):
        # disable triggers
        pvs2set = [trg+':State-Sel' for trg in self.TRIGGERS]
        self._set_pvs(pvs2set, TRG_DSBL_VAL)

        # wait for triggers to be disabled
        pvs2wait = [trg+':State-Sts' for trg in self.TRIGGERS]
        retval = self._wait_pvs(pvs2wait, TRG_DSBL_VAL)
        if not retval[0]:
            text = 'Check for BO Mags Triggers to be disabled timed\n'\
                   'out without success!\nVerify BO Mags Triggers!'
            return [False, text, retval[1]]

        # wait duration of a ramp for PS change opmode
        _time.sleep(0.5)

        # set slowref
        pvs2set = [psn+':OpMode-Sel' for psn in self.DEVICES]
        self._set_pvs(pvs2set, PS_OPM_SLWREF)

        # wait for PS change opmode
        pvs2wait = [psn+':OpMode-Sts' for psn in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, PS_STS_SLWREF)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode SlowRef\n'\
                   'timed out without success!\nVerify BO PS!'
            return [False, text, retval[1]]

        # set current to zero
        pvs2set = [psn+':Current-SP' for psn in self.DEVICES]
        self._set_pvs(pvs2set, 0.0)

        # wait current change to zero
        pvs2wait = [psn+':Current-RB' for psn in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, 0.0)
        if not retval[0]:
            text = 'Check for BO PS to be with current zero\n'\
                   'timed out without success!\nVerify BO PS!'
            return [False, text, retval[1]]

        return True, '', []

    def turn_on(self):
        # set rmpwfm
        pvs2set = [psn+':OpMode-Sel' for psn in self.DEVICES]
        self._set_pvs(pvs2set, PS_OPM_RMPWFM)

        # wait for PS change opmode
        pvs2wait = [psn+':OpMode-Sts' for psn in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, PS_STS_RMPWFM)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode RmpWfm\n'\
                   'timed out without success!\nVerify BO PS!'
            return [False, text, retval[1]]

        # set WfmUpdateAuto
        pvs2set = [psn+':WfmUpdateAuto-Sel' for psn in self.DEVICES]
        self._set_pvs(pvs2set, PS_ENBL_VAL)

        # wait for PS WfmUpdateAuto to be enabled
        pvs2wait = [psn+':WfmUpdateAuto-Sts' for psn in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, PS_ENBL_VAL)
        if not retval[0]:
            text = 'Check for BO PS WfmUpdateAuto to be enable\n'\
                   'timed out without success!\nVerify BO PS!'
            return [False, text, retval[1]]

        # configure trigger source
        self._set_pvs('BO-Glob:TI-Mags-Fams:Src-Sel', BO_FAMS_EVT_INDEX)
        self._set_pvs('BO-Glob:TI-Mags-Corrs:Src-Sel', BO_CORRS_EVT_INDEX)

        # wait for trigger source to be configured
        retval1 = self._wait_pvs(
            'BO-Glob:TI-Mags-Fams:Src-Sel', BO_FAMS_EVT_INDEX)
        retval2 = self._wait_pvs(
            'BO-Glob:TI-Mags-Corrs:Src-Sel', BO_CORRS_EVT_INDEX)
        if not retval1[0] or not retval2[0]:
            text = 'Check for BO Mags Triggers to be in RmpBO event\n'\
                   'timed out without success!\nVerify BO Mags Triggers!'
            problems = retval1[1]
            problems.extend(retval2[1])
            return [False, text, problems]

        # enable triggers
        pvs2set = [trg+':State-Sel' for trg in self.TRIGGERS]
        self._set_pvs(pvs2set, TRG_ENBL_VAL)

        # wait for triggers to be enable
        pvs2wait = [trg+':State-Sts' for trg in self.TRIGGERS]
        retval = self._wait_pvs(pvs2wait, TRG_ENBL_VAL)
        if not retval[0]:
            text = 'Check for BO Mags Triggers to be enable timed\n'\
                   'out without success!\nVerify BO Mags Triggers!'
            return [False, text, retval[1]]

        return True, '', []


class BORFRampStandbyHandler(_BaseHandler):
    """Booster RF Ramp Standby Mode Handler."""

    def __init__(self):
        """Initialize."""
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        _pvs = dict()
        pvnames = ['BR-RF-DLLRF-01:RmpEnbl-Sel',
                   'BR-RF-DLLRF-01:RmpEnbl-Sts']
        for pvn in pvnames:
            _pvs[pvn] = _PV(_vaca_prefix+pvn, connection_timeout=0.05)
        self._pvs.update(_pvs)

    def turn_off(self):
        # set RF ramp to disable
        self._set_pvs('BR-RF-DLLRF-01:RmpEnbl-Sel', TRG_DSBL_VAL)

        # wait for RF ramp to be disable
        retval = self._wait_pvs('BR-RF-DLLRF-01:RmpEnbl-Sts', TRG_DSBL_VAL)
        if not retval[0]:
            text = 'Check for BO RF Ramp to be disabled timed\n'\
                   'out without success!\nVerify BO RF Ramp!'
            return [False, text, retval[1]]

        return True, '', []

    def turn_on(self):
        # set RF ramp to enabled
        self._set_pvs('BR-RF-DLLRF-01:RmpEnbl-Sel', TRG_ENBL_VAL)

        # wait for RF ramp to be enabled
        retval = self._wait_pvs('BR-RF-DLLRF-01:RmpEnbl-Sts', TRG_ENBL_VAL)
        if not retval[0]:
            text = 'Check for BO RF Ramp to be enabled timed\n'\
                   'out without success!\nVerify BO RF Ramp!'
            return [False, text, retval[1]]

        return True, '', []


class PUStandbyHandler(_BaseHandler):
    """Pulsed magnets Standby Mode Handler."""

    DEVICES = PSSearch.get_psnames({'dis': 'PU', 'dev': '.*(Kckr|Sept)'})
    TRIGGERS = [dev.replace('PU', 'TI') for dev in DEVICES]

    def __init__(self):
        """Initialize."""
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()
        ppties = ['Pulse-Sel', 'Pulse-Sts', 'PwrState-Sel', 'PwrState-Sts']
        for pun in self.DEVICES:
            for ppty in ppties:
                pvname = pun+':'+ppty
                _pvs[pvname] = _PV(
                    _vaca_prefix+pvname, connection_timeout=0.05)
        self._pvs.update(_pvs)

    def turn_off(self):
        # set pulse off
        pvs2set = [pun+':Pulse-Sel' for pun in self.DEVICES]
        self._set_pvs(pvs2set, PU_DSBL_VAL, wait=0.5)

        # wait for PU pulse to be off
        pvs2wait = [pun+':Pulse-Sts' for pun in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, PU_DSBL_VAL)
        if not retval[0]:
            text = 'Check for PU Pulse to be disabled\n'\
                   'timed out without success!\nVerify PU!'
            return [False, text, retval[1]]

        # set power state off
        pvs2set = [pun+':PwrState-Sel' for pun in self.DEVICES]
        self._set_pvs(pvs2set, PU_DSBL_VAL, wait=1)

        # wait for PU power state to be off
        pvs2wait = [pun+':PwrState-Sts' for pun in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, PU_DSBL_VAL)
        if not retval[0]:
            text = 'Check for PU PwrState to be off\n'\
                   'timed out without success!\nVerify PU!'
            return [False, text, retval[1]]

        return True, '', []

    def turn_on(self):
        # set pulse on
        pvs2set = [pun+':Pulse-Sel' for pun in self.DEVICES
                   if 'InjDpKckr' not in pun]
        self._set_pvs(pvs2set, PU_ENBL_VAL, wait=0.5)

        # wait for PU pulse to be on
        pvs2wait = [pun+':Pulse-Sts' for pun in self.DEVICES
                    if 'InjDpKckr' not in pun]
        retval = self._wait_pvs(pvs2wait, PU_ENBL_VAL)
        if not retval[0]:
            text = 'Check for PU Pulse to be enabled\n'\
                   'timed out without success!\nVerify PU!'
            return [False, text, retval[1]]

        # set power state on
        pvs2set = [pun+':PwrState-Sel' for pun in self.DEVICES
                   if 'InjDpKckr' not in pun]
        self._set_pvs(pvs2set, PU_ENBL_VAL, wait=1)

        # wait for PU power state to be on
        pvs2wait = [pun+':PwrState-Sts' for pun in self.DEVICES
                    if 'InjDpKckr' not in pun]
        retval = self._wait_pvs(pvs2wait, PU_ENBL_VAL)
        if not retval[0]:
            text = 'Check for PU PwrState to be on\n'\
                   'timed out without success!\nVerify PU!'
            return [False, text, retval[1]]

        return True, '', []


class InjBOStandbyHandler(_BaseHandler):
    """InjBO Event Standby Mode Handler."""

    def __init__(self):
        """Initialize."""
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        _pvs = dict()
        ppties = ['InjBOMode-Sel', 'InjBOMode-Sts', 'UpdateEvt-Cmd']
        for ppty in ppties:
            pvname = EVG_NAME + ':' + ppty
            _pvs[pvname] = _PV(_vaca_prefix+pvname, connection_timeout=0.05)
        self._pvs.update(_pvs)

    def turn_off(self):
        # disable injbo
        self._set_pvs(EVG_NAME+':InjBOMode-Sel', EVT_DSBL_VAL)

        # wait for injbo to be disabled
        retval = self._wait_pvs(EVG_NAME+':InjBOMode-Sts', EVT_DSBL_VAL)
        if not retval[0]:
            text = 'Check for InjBO Event to be disabled timed\n'\
                   'out without success!\nVerify InjBO Event!'
            return [False, text, retval[1]]

        # update events
        self._set_pvs(EVG_NAME+':UpdateEvt-Cmd', 1)

        return True, '', []

    def turn_on(self):
        # set injbo to Continuous table
        self._set_pvs(EVG_NAME+':InjBOMode-Sel', EVT_CONT_VAL)

        # wait for injbo to be in Continuous Table
        retval = self._wait_pvs(EVG_NAME+':InjBOMode-Sts', EVT_CONT_VAL)
        if not retval[0]:
            text = 'Check for InjBO Event to be in Continuous table\n'\
                   'timed out without success!\nVerify InjBO Event!'
            return [False, text, retval[1]]

        # update events
        self._set_pvs(EVG_NAME+':UpdateEvt-Cmd', 1)

        return True, '', []
