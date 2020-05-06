
from copy import deepcopy as _dcopy
import time as _time
from datetime import datetime as _datetime
from qtpy.QtCore import Signal, QThread
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.cycle import PSCycler, LinacPSCycler, CycleController


TIMEOUT_CHECK = 10
TIMEOUT_SLEEP = 0.1
TIMEOUT_CONN = 0.5


class BaseTask(QThread):
    """Base Task."""

    _cyclers = dict()
    _controller = None
    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()
    updated = Signal(str, bool, bool, bool)

    def __init__(self, parent=None, psnames=list(), timing=None,
                 need_controller=False, create_new_controller=False):
        super().__init__(parent)
        self._psnames = psnames
        self._timing = timing
        if need_controller:
            if not BaseTask._controller or create_new_controller:
                cyclers = dict()
                for ps in psnames:
                    cyclers[ps] = BaseTask._cyclers[ps]
                BaseTask._controller = CycleController(
                    cyclers=cyclers, timing=timing, logger=self)
            else:
                BaseTask._controller.logger = self
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._psnames)

    def duration(self):
        """Return task maximum duration."""
        raise NotImplementedError

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Run task."""
        if not self._quit_task:
            self._interrupted = False
            self.function()
        if not self._interrupted:
            self.completed.emit()

    def update(self, message, done, warning, error):
        now = _datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message, done, warning, error)

    def function(self):
        """Must be reimplemented in each class."""
        raise NotImplementedError

    def _set(self, method, **kwargs):
        """Set."""
        for ps in self._psnames:
            self.currentItem.emit(ps)
            cycler = BaseTask._cyclers[ps]
            if not cycler.wait_for_connection(TIMEOUT_CONN):
                self.itemDone.emit(ps, False)
                continue
            func = getattr(cycler, method)
            func(**kwargs)
            self.itemDone.emit(ps, True)
            if self._quit_task:
                self._interrupted = True
                break

    def _check(self, method, timeout=TIMEOUT_CHECK, **kwargs):
        """Check."""
        self._interrupted = False
        need_check = _dcopy(self._psnames)
        t = _time.time()
        while _time.time() - t < timeout:
            for ps in self._psnames:
                if ps not in need_check:
                    continue
                cycler = BaseTask._cyclers[ps]
                func = getattr(cycler, method)
                if func(**kwargs):
                    self.currentItem.emit(ps)
                    need_check.remove(ps)
                    self.itemDone.emit(ps, True)
                if self._quit_task:
                    self._interrupted = True
                    break
            if (not need_check) or (self._quit_task):
                break
            _time.sleep(TIMEOUT_SLEEP)
        for ps in need_check:
            self.currentItem.emit(ps)
            self.itemDone.emit(ps, False)


class CreateCyclers(BaseTask):
    """Create cyclers."""

    def function(self):
        """Create cyclers."""
        for psname in self._psnames:
            self.currentItem.emit(psname)
            if psname not in BaseTask._cyclers:
                if PVName(psname).sec == 'LI':
                    c = LinacPSCycler(psname)
                else:
                    c = PSCycler(psname)
                BaseTask._cyclers[psname] = c
            self.itemDone.emit(psname, True)
            if self._quit_task:
                self._interrupted = True
                break


class VerifyPS(BaseTask):
    """Verify power supply initial state."""

    def size(self):
        """Return task size."""
        return 2*len(self._psnames)

    def function(self):
        """Set power supplies to cycling."""
        self._check(method='check_on')
        self._check(method='check_intlks')


class ZeroPSCurrent(BaseTask):
    """Set power supply current to zero."""

    def function(self):
        """Set power supplies current to zero."""
        self._set(method='set_current_zero')


class ResetPSOpMode(BaseTask):
    """Set power supply to SlowRef."""

    def function(self):
        """Set power supplies to cycling."""
        self._set(method='set_opmode_slowref')


class RestoreTiming(BaseTask):
    """Restore timing initial state."""

    def size(self):
        """Return task size."""
        return 2

    def function(self):
        self.itemDone.emit('timing', True)
        self._timing.restore_initial_state()
        self.itemDone.emit('timing', True)


class PreparePSParams(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_parameters()


class PreparePSOpMode(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_opmode()


class PrepareTiming(BaseTask):
    """Prepare timing to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_timing_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_timing_max_duration

    def function(self):
        self._controller.prepare_timing()


class CycleTrims(BaseTask):
    """Cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.cycle_trims_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.cycle_trims_max_duration

    def function(self):
        self._controller.cycle_all_trims()


class Cycle(BaseTask):
    """Cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.cycle_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.cycle_max_duration

    def function(self):
        self._controller.cycle()
