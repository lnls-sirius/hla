
from copy import deepcopy as _dcopy
import time as _time
from datetime import datetime as _datetime
from qtpy.QtCore import Signal, QThread
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import PSSearch
from siriuspy.cycle import PSCycler, LinacPSCycler, PSCyclerFBP, FOFBPSCycler,\
    CycleController


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
                 need_controller=False, isadv=False):
        super().__init__(parent)
        self._psnames = psnames
        self._timing = timing
        if need_controller:
            cyclers = dict()
            for ps in psnames:
                cyclers[ps] = BaseTask._cyclers[ps]
            if not BaseTask._controller:
                BaseTask._controller = CycleController(
                    cyclers=cyclers, timing=timing, logger=self,
                    isadv=isadv)
            else:
                BaseTask._controller.cyclers = cyclers
                BaseTask._controller.timing = timing
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
                elif PSSearch.conv_psname_2_psmodel(psname) == 'FOFB_PS':
                    c = FOFBPSCycler(psname)
                elif PSSearch.conv_psname_2_psmodel(psname) == 'FBP':
                    c = PSCyclerFBP(psname)
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
        """Verify if PS is ready for cycle."""
        self._check(method='check_on')
        self._check(method='check_intlks')


class SaveTiming(BaseTask):
    """Save timing initial state."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.save_timing_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.save_timing_max_duration

    def function(self):
        self._controller.save_timing_initial_state()


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


class PreparePSSOFBMode(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_sofbmode_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_sofbmode_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_sofbmode()


class PreparePSOpModeSlowRef(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_opmode_slowref_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_opmode_slowref_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_opmode_slowref()


class PreparePSCurrentZero(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_current_zero_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_current_zero_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_current_zero()


class PreparePSParams(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_params_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_params_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_parameters()


class PreparePSOpModeCycle(BaseTask):
    """Prepare power suplies to cycle."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.prepare_ps_opmode_cycle_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_ps_opmode_cycle_max_duration

    def function(self):
        self._controller.prepare_pwrsupplies_opmode_cycle()


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
        self._controller.cycle_trims()


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


class RestoreTiming(BaseTask):
    """Restore timing initial state."""

    def __init__(self, **kwargs):
        super().__init__(need_controller=True, **kwargs)

    def size(self):
        return self._controller.restore_timing_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.restore_timing_max_duration

    def function(self):
        self._controller.restore_timing_initial_state()
