import time as _time
from epics import PV as _PV

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch, HLTimeSearch
from siriuspy.timesys.csdev import Const as TIConst, \
    get_hl_trigger_database as _get_trig_db
from siriuspy.pwrsupply.csdev import Const as PSConst

_BO_FAMS_TRIG_DB = _get_trig_db('BO-Glob:TI-Mags-Fams')
_BO_CORRS_TRIG_DB = _get_trig_db('BO-Glob:TI-Mags-Corrs')

TIMEOUT_WAIT = 3
TRG_ENBL_VAL = TIConst.DsblEnbl.Enbl
TRG_DSBL_VAL = TIConst.DsblEnbl.Dsbl
PU_ENBL_VAL = PSConst.DsblEnbl.Enbl
PU_DSBL_VAL = PSConst.DsblEnbl.Dsbl
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

    def _set_pvs(self, pvnames, value):
        """Set PVs to value."""
        for pvname in pvnames:
            pv = self._pvs[pvname]
            if pv.wait_for_connection():
                pv.put(value)

    def _wait_pvs(self, pvnames, value):
        """Wait for PVs to reach value."""
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
                    prob.append(str(_PVName(pvn).device_name))
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
            text = 'Check for LI LLRF Feedback Mode timed\n'\
                   'out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        # turn integral off
        pvs2set = [dev+':SET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_DSBL_VAL)

        # wait for integral to turn off
        pvs2wait = [dev+':GET_INTEGRAL_ENABLE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_DSBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Integral Mode timed\n'\
                   'out without success\nVerify LI LLRF!'
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
            text = 'Check for LI LLRF Integral Mode timed\n'\
                   'out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        # turn feedback on
        pvs2set = [dev+':SET_FB_MODE' for dev in self.DEVICES]
        self._set_pvs(pvs2set, LILLRF_ENBL_VAL)

        # wait for feedback to turn on
        pvs2wait = [dev+':GET_FB_MODE' for dev in self.DEVICES]
        retval = self._wait_pvs(pvs2wait, LILLRF_ENBL_VAL)
        if not retval[0]:
            text = 'Check for LI LLRF Feedback Mode timed\n'\
                   'out without success\nVerify LI LLRF!'
            return [False, text, retval[1]]

        return True, '', []


class BORampStandbyHandler(_BaseHandler):
    """Booster PS Ramp Standby Mode Handler."""

    DEVICES = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})

    def __init__(self):
        """Init."""
        self._triggers = HLTimeSearch.get_hl_triggers(
            {'sec': 'BO', 'dev': 'Mags'})
        self._pvs = dict()
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()
        pspropties = ['OpMode-Sel', 'OpMode-Sts', 'Current-SP', 'Current-RB']
        for psn in self.DEVICES:
            for propty in pspropties:
                pvname = psn+':'+propty
                _pvs[pvname] = _PV(
                    _vaca_prefix+pvname, connection_timeout=0.05)

        for trg in self._triggers:
            pvname = trg+':State-Sts'
            _pvs[pvname] = _PV(_vaca_prefix+pvname, connection_timeout=0.05)

        self._pvs.update(_pvs)

    def turn_off(self):
        # wait for triggers disable
        pvs2wait = [trg+':State-Sts' for trg in self._triggers]
        retval = self._wait_pvs(pvs2wait, TRG_DSBL_VAL)
        if not retval[0]:
            text = 'Check for BO Triggers to be disabled\n'\
                   'timed out without success!\nVerify BO Mags Triggers!'
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

        return True, '', []
