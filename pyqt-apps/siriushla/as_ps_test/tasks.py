from copy import deepcopy as _dcopy
import time as _time
from epics import PV as _PV
from qtpy.QtCore import Signal, QThread
from siriuspy.search import HLTimeSearch as _HLTimeSearch, \
    PSSearch as _PSSearch
from siriuspy.csdev import Const
from siriuspy.namesys import Filter, SiriusPVName as _PVName
from .conn import TesterDCLink, TesterDCLinkFBP, TesterPS, TesterPSLinac, \
    TesterPUKckr, TesterPUSept, DEFAULT_CAP_BANK_VOLT


TIMEOUT_CHECK = 10
TIMEOUT_SLEEP = 0.1
TIMEOUT_CONN = 0.5


class BaseTask(QThread):
    """Base Task."""

    _testers = dict()
    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, state=None, is_test=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._state = state
        self._is_test = is_test
        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._devices)

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        """Run task."""
        if not self._quit_task:
            self.function()
        self.completed.emit()

    def function(self):
        """Must be reimplemented in each class."""
        raise NotImplementedError

    def _set(self, method, **kwargs):
        """Set."""
        for dev in self._devices:
            self.currentItem.emit(dev)
            tester = BaseTask._testers[dev]
            if not tester.wait_for_connection(TIMEOUT_CONN):
                self.itemDone.emit(dev, False)
                continue
            func = getattr(tester, method)
            func(**kwargs)
            self.itemDone.emit(dev, True)
            if self._quit_task:
                break

    def _check(self, method, timeout=TIMEOUT_CHECK, **kwargs):
        """Check."""
        need_check = _dcopy(self._devices)
        t = _time.time()
        while _time.time() - t < timeout:
            for dev in self._devices:
                if dev not in need_check:
                    continue
                tester = BaseTask._testers[dev]
                func = getattr(tester, method)
                if func(**kwargs):
                    self.currentItem.emit(dev)
                    need_check.remove(dev)
                    self.itemDone.emit(dev, True)
                if self._quit_task:
                    break
            if (not need_check) or (self._quit_task):
                break
            _time.sleep(TIMEOUT_SLEEP)
        for dev in need_check:
            self.currentItem.emit(dev)
            self.itemDone.emit(dev, False)


class CreateTesters(BaseTask):

    def function(self):
        for dev in self._devices:
            self.currentItem.emit(dev)
            if dev not in BaseTask._testers:
                devname = _PVName(dev)
                if devname.sec == 'LI':
                    t = TesterPSLinac(dev)
                elif _PSSearch.conv_psname_2_psmodel(dev) == 'FBP_DCLink':
                    t = TesterDCLinkFBP(dev)
                elif 'bo-dclink' in _PSSearch.conv_psname_2_pstype(dev):
                    t = TesterDCLink(dev)
                elif devname.dis == 'PS':
                    t = TesterPS(dev)
                elif devname.dis == 'PU' and 'Kckr' in devname.dev:
                    t = TesterPUKckr(dev)
                elif devname.dis == 'PU' and 'Sept' in devname.dev:
                    t = TesterPUSept(dev)
                else:
                    raise NotImplementedError(
                        'There is no Tester defined to '+dev+'.')
                BaseTask._testers[dev] = t
            self.itemDone.emit(dev, True)
            if self._quit_task:
                break


class CheckStatus(BaseTask):
    """Check Status."""

    def function(self):
        """Check status."""
        self._check(method='check_status')


class ResetIntlk(BaseTask):
    """Reset Interlocks."""

    def function(self):
        """Reset."""
        self._set(method='reset')
        if Filter.process_filters(
                pvnames=self._devices, filters={'sec': 'SI', 'sub': 'Fam'}):
            _time.sleep(2.0)


class CheckIntlk(BaseTask):
    """Check Interlocks."""

    def function(self):
        """Check interlocks."""
        self._check(method='check_intlk')


class SetOpModeSlowRef(BaseTask):
    """Set PS OpMode to SlowRef."""

    def function(self):
        """Set PS OpMode to SlowRef."""
        self._set(method='set_slowref')


class CheckOpModeSlowRef(BaseTask):
    """Check if PS OpMode is in SlowRef."""

    def function(self):
        """Check PS OpMode in SlowRef."""
        self._check(method='check_slowref')


class SetPwrState(BaseTask):
    """Set PS PwrState."""

    def function(self):
        """Set PS PwrState."""
        self._set(method='set_pwrstate', state=self._state)


class CheckPwrState(BaseTask):
    """Check PS PwrState."""

    def function(self):
        """Check PS PwrState."""
        self._check(method='check_pwrstate', state=self._state,
                    timeout=3*TIMEOUT_CHECK)


class SetPulse(BaseTask):
    """Set PU Pulse."""

    def function(self):
        """Set PU Pulse."""
        self._set(method='set_pulse', state=self._state)


class CheckPulse(BaseTask):
    """Check PU Pulse."""

    def function(self):
        """Check PU Pulse."""
        self._check(method='check_pulse', state=self._state,
                    timeout=TIMEOUT_CHECK)


class CheckInitOk(BaseTask):
    """Check if PS OpMode is in SlowRef."""

    def function(self):
        """Check PS OpMode in SlowRef."""
        self._check(method='check_init_ok', timeout=3*TIMEOUT_CHECK)


class SetCtrlLoop(BaseTask):
    """Set PS CtrlLoop."""

    def function(self):
        """Set PS CtrlLoop."""
        self._set(method='set_ctrlloop')


class CheckCtrlLoop(BaseTask):
    """Check PS CtrlLoop."""

    def function(self):
        """Check PS CtrlLoop."""
        self._check(method='check_ctrlloop')


class SetCapBankVolt(BaseTask):
    """Set capacitor bank voltage."""

    def function(self):
        """Set DCLink Capacitor Bank Voltage."""
        self._set(method='set_capvolt')


class CheckCapBankVolt(BaseTask):
    """Check capacitor bank voltage."""

    def function(self):
        """Check DCLink Capacitor Bank Voltage."""
        psn = {k for k in DEFAULT_CAP_BANK_VOLT.keys()
               if k != 'FBP_DCLink'}
        if any(n in self._devices for n in psn):
            timeout = 6*TIMEOUT_CHECK
        else:
            timeout = TIMEOUT_CHECK
        self._check(method='check_capvolt', timeout=timeout)


class SetCurrent(BaseTask):
    """Set current value."""

    def function(self):
        """Set PS Current."""
        self._set(method='set_current', test=self._is_test)


class CheckCurrent(BaseTask):
    """Check current value."""

    def function(self):
        """Check PS Current."""
        psn = {'SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2'}
        if any(n in self._devices for n in psn):
            timeout = 4.1*TIMEOUT_CHECK
        else:
            timeout = 2.1*TIMEOUT_CHECK
        self._check(method='check_current',
                    timeout=timeout,
                    test=self._is_test)


class SetVoltage(BaseTask):
    """Set voltage value."""

    def function(self):
        """Set PU Voltage."""
        self._set(method='set_voltage', test=self._is_test)


class CheckVoltage(BaseTask):
    """Check voltage value."""

    def function(self):
        """Check PU Voltage."""
        if self._is_test:
            timeout = 10
        else:
            if 'BO-48D:PU-EjeKckr' in self._devices:
                timeout = 45
            elif 'SI-01SA:PU-InjNLKckr' in self._devices:
                timeout = 35
            elif 'SI-01SA:PU-InjDpKckr' in self._devices:
                timeout = 17
            else:
                timeout = 10
        self._check(method='check_voltage', timeout=timeout,
                    test=self._is_test)


class TriggerTask(QThread):
    """Base task to handle triggers."""

    initial_triggers_state = dict()

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, parent=None, restore_initial_value=False,
                 dis='PS', state='on', devices=list()):
        """Constructor."""
        super().__init__(parent)
        self._dis = dis
        filt = {'dev': 'Mags'} if dis == 'PS' else {'dev': '.*(Kckr|Sept).*'}
        self._triggers = _HLTimeSearch.get_hl_triggers(filters=filt)
        self._pvs_sp = {trg: _PV(trg+':State-Sel', connection_timeout=0.05)
                        for trg in self._triggers}
        self._pvs_rb = {trg: _PV(trg+':State-Sts', connection_timeout=0.05)
                        for trg in self._triggers}

        for trg, pv in self._pvs_rb.items():
            pv.get()  # force connection
            if trg not in TriggerTask.initial_triggers_state.keys():
                TriggerTask.initial_triggers_state[trg] = pv.value

        if restore_initial_value:
            self.trig2val = {
                k: v for k, v in TriggerTask.initial_triggers_state.items()
                if k in self._triggers}
        else:
            val = Const.DsblEnbl.Enbl if state == 'on' else Const.DsblEnbl.Dsbl
            self.trig2val = {trig: val for trig in self._triggers}

        self._devices = devices
        self._trig2ctrl = self._get_trigger_by_psname(self._devices)

        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._triggers)

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        """Run task."""
        if not self._quit_task:
            self.function()
        self.completed.emit()

    def function(self, ):
        raise NotImplementedError

    def _get_trigger_by_psname(self, devices):
        """Return triggers corresponding to devices."""
        devices = set(devices)
        triggers = set()
        if self._dis == 'PS':
            for trig in self._triggers:
                channels_set = set(_HLTimeSearch.get_hl_trigger_channels(trig))
                dev_set = {ch.device_name for ch in channels_set}
                if devices & dev_set:
                    triggers.add(trig)
        else:
            for dev in devices:
                trig = _PVName(dev).substitute(dis='TI')
                triggers.add(trig)
        return triggers

    def _set(self):
        for trig in self._trig2ctrl:
            self.currentItem.emit(trig)
            pv = self._pvs_sp[trig]
            val = self.trig2val[trig]
            # pv.value = val
            print(pv.pvname, val)
            self.itemDone.emit(trig, True)

    def _check(self):
        need_check = _dcopy(self._trig2ctrl)
        t0 = _time.time()
        while _time.time() - t0 < TIMEOUT_CHECK/2:
            for trig in self._trig2ctrl:
                if trig not in need_check:
                    continue
                pv = self._pvs_rb[trig]
                val = self.trig2val[trig]
                if pv.value == val:
                    self.currentItem.emit(trig)
                    self.itemDone.emit(trig, True)
                    need_check.remove(trig)
                if self._quit_task:
                    break
            if (not need_check) or (self._quit_task):
                break
            _time.sleep(TIMEOUT_SLEEP)
        for trig in need_check:
            self.currentItem.emit(trig)
            self.itemDone.emit(trig, False)


class SetTriggerState(TriggerTask):
    """Set magnet trigger state."""

    def function(self):
        self._set()


class CheckTriggerState(TriggerTask):
    """Check magnet trigger state."""

    def function(self):
        self._check()
