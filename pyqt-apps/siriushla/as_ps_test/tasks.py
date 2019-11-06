import time as _time

from qtpy.QtCore import Signal, QThread


TIMEOUT_CHECK = 10
TIMEOUT_SLEEP = 0.1


class BaseTask(QThread):
    """Setter."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, testers, state=None, is_test=None, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._testers = testers
        self._state = state
        self._is_test = is_test
        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._testers.keys())

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
        for dev, tester in self._testers.items():
            self.currentItem.emit(dev)
            func = getattr(tester, method)
            func(**kwargs)
            self.itemDone.emit(dev, True)
            if self._quit_task:
                break

    def _check(self, method, timeout=TIMEOUT_CHECK, **kwargs):
        """Check."""
        need_check = list(self._testers.keys())
        t = _time.time()
        while _time.time() - t < timeout:
            for dev, tester in self._testers.items():
                if dev not in need_check:
                    continue
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


class ResetIntlk(BaseTask):
    """Reset Interlocks."""

    def function(self):
        """Reset PS."""
        self._set(method='reset')


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
                    timeout=TIMEOUT_CHECK,
                    test=self._is_test)
