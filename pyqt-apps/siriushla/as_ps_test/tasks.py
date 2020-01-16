from copy import deepcopy as _dcopy
import time as _time
from epics import PV as _PV
from qtpy.QtCore import Signal, QThread
from siriuspy.search import HLTimeSearch as _HLTimeSearch, \
    PSSearch as _PSSearch
from siriuspy.csdevice.util import Const
from siriuspy.namesys import Filter, SiriusPVName as _PVName
from .conn import TesterDCLink, TesterDCLinkFBP, TesterPS, TesterPSLinac


TIMEOUT_CHECK = 10
TIMEOUT_SLEEP = 0.1
TIMEOUT_CONN = 0.5


class BaseTask(QThread):
    """Base Task."""

    _testers = dict()
    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, state=None, is_test=None, parent=None):
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
                if _PVName(dev).sec == 'LI':
                    t = TesterPSLinac(dev)
                elif _PSSearch.conv_psname_2_psmodel(dev) == 'FBP_DCLink':
                    t = TesterDCLinkFBP(dev)
                elif 'bo-dclink' in _PSSearch.conv_psname_2_pstype(dev):
                    t = TesterDCLink(dev)
                elif _PVName(dev).dis == 'PS':
                    t = TesterPS(dev)
                BaseTask._testers[dev] = t
            self.itemDone.emit(dev, True)
            if self._quit_task:
                break


class CheckStatus(BaseTask):
    """Check Status."""

    def function(self):
        self._check(method='check_status')


class ResetIntlk(BaseTask):
    """Reset Interlocks."""

    def function(self):
        """Reset PS."""
        self._set(method='reset')
        if Filter.process_filters(
                pvnames=self._devices, filters={'sec': 'SI', 'sub': 'Fam'}):
            _time.sleep(2.0)


class CheckIntlk(BaseTask):
    """Check Interlocks."""

    def function(self):
        """Check PS interlocks."""
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
        self._check(method='check_capvolt', timeout=6*TIMEOUT_CHECK)


class SetCurrent(BaseTask):
    """Set current value and check if it RB is achieved."""

    def function(self):
        """Set PS Current."""
        self._set(method='set_current', test=self._is_test)


class CheckCurrent(BaseTask):
    """Set current value and check if it RB is achieved."""

    def function(self):
        """Set PS Current."""
        self._check(method='check_current',
                    timeout=2.2*TIMEOUT_CHECK,
                    test=self._is_test)


class TriggerTask(QThread):
    """Base task to handle triggers."""

    initial_triggers_state = dict()

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, restore_initial_value=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._triggers = _HLTimeSearch.get_hl_triggers(filters={'dev': 'Mags'})
        self._pvs = {trg: _PV(trg + ':State-Sel') for trg in self._triggers}

        for trg, pv in self._pvs.items():
            pv.get()  # force connection
            if trg not in TriggerTask.initial_triggers_state.keys():
                TriggerTask.initial_triggers_state[trg] = pv.value

        if restore_initial_value:
            self.trig2val = TriggerTask.initial_triggers_state
        else:
            self.trig2val = {trig: Const.DsblEnbl.Dsbl
                             for trig in self._pvs.keys()}
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

    def function(self):
        raise NotImplementedError


class SetTriggerState(TriggerTask):
    """Disable magnets triggers."""

    def function(self):
        for trig, val in self.trig2val.items():
            self.currentItem.emit(trig)
            pv = self._pvs[trig]
            pv.value = val
            self.itemDone.emit(trig, True)


class CheckTriggerState(TriggerTask):
    """Disable magnets triggers."""

    def function(self):
        need_check = _dcopy(self.trig2val)
        t0 = _time.time()
        while _time.time() - t0 < TIMEOUT_CHECK/2:
            for trig, val in self.trig2val.items():
                if trig not in need_check:
                    continue
                pv = self._pvs[trig]
                if pv.value == val:
                    self.currentItem.emit(trig)
                    self.itemDone.emit(trig, True)
                    need_check.pop(trig)
                if self._quit_task:
                    break
            if (not need_check) or (self._quit_task):
                break
            _time.sleep(TIMEOUT_SLEEP)
        for trig in need_check:
            self.currentItem.emit(trig)
            self.itemDone.emit(trig, False)
