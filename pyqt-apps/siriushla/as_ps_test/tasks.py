import time as _time
from epics import PV as _PV

from qtpy.QtCore import Signal, QThread

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.csdevice.pwrsupply import Const as _PSC
from siriuspy.search import MASearch, PSSearch
from .dclinks_data import DEFAULT_CAP_BANK_VOLT


TIMEOUT_CHECK = 10
TIMEOUT_SLEEP = 0.1
TEST_TOLERANCE = 1e-1


class ResetIntlk(QThread):
    """Reset Interlocks."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = [_PV(VACA_PREFIX + dev + ':Reset-Cmd')
                     for dev in devices if 'LI' not in dev]
        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        """Execute task."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                pv.get()  # force connection
                if pv.connected:
                    pv.put(1)
                    _time.sleep(TIMEOUT_SLEEP)
                self.itemDone.emit()
        self.completed.emit()


class CheckIntlk(QThread):
    """Check Interlocks."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = list()
        for dev in devices:
            if 'LI' in dev:
                self._pvs.append(_PV(VACA_PREFIX + dev + ':interlock'))
            else:
                self._pvs.append(_PV(VACA_PREFIX + dev + ':IntlkHard-Mon'))
                self._pvs.append(_PV(VACA_PREFIX + dev + ':IntlkSoft-Mon'))
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS on."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                t = _time.time()
                is_ok = False
                pv.get()  # force connection
                if pv.connected:
                    while _time.time() - t < TIMEOUT_CHECK:
                        if (pv.value == 0 and 'LI' not in dev) or \
                                (pv.value < 55 and 'LI' in dev):
                            is_ok = True
                            break
                        if self._quit_task:
                            break
                self.itemDone.emit(dev, is_ok)
                _time.sleep(TIMEOUT_SLEEP)
                if self._quit_task:
                    break
        self.completed.emit()


class SetOpModeSlowRef(QThread):
    """Set PS OpMode to SlowRef."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._opmode = _PSC.OpMode.SlowRef
        self._pvs = [_PV(VACA_PREFIX + dev + ':OpMode-Sel')
                     for dev in devices if 'LI' not in dev]
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS OpMode to SlowRef."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                pv.get()  # force connection
                if pv.connected:
                    pv.put(self._opmode)
                    _time.sleep(TIMEOUT_SLEEP)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()


class CheckOpModeSlowRef(QThread):
    """Check if PS OpMode is in SlowRef."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._state = _PSC.States.SlowRef
        self._pvs = [_PV(VACA_PREFIX + dev + ':OpMode-Sts')
                     for dev in devices if 'LI' not in dev]
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Check PS OpMode in SlowRef."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                pv.get()  # force connection
                t = _time.time()
                is_ok = False
                if pv.connected:
                    while _time.time() - t < 3*TIMEOUT_CHECK:
                        if pv.get() == self._state:
                            is_ok = True
                            break
                        if self._quit_task:
                            break
                self.itemDone.emit(dev, is_ok)
                _time.sleep(TIMEOUT_SLEEP)
                if self._quit_task:
                    break
        self.completed.emit()


class SetPwrState(QThread):
    """Set PS PwrState."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices, state, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._state = (_PSC.PwrStateSel.On if state == 'on'
                       else _PSC.PwrStateSel.Off)
        self._pvs = list()
        for dev in devices:
            ppty = ':setpwm' if 'LI' in dev else ':PwrState-Sel'
            self._pvs.append(_PV(VACA_PREFIX + dev + ppty))
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS PwrState."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                pv.get()  # force connection
                if pv.connected:
                    pv.put(self._state)
                    _time.sleep(TIMEOUT_SLEEP)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()


class CheckPwrState(QThread):
    """Check PS PwrState."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, state, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._state = (_PSC.PwrStateSts.On if state == 'on'
                       else _PSC.PwrStateSts.Off)
        self._pvs = list()
        for dev in devices:
            ppty = ':rdpwm' if 'LI' in dev else ':PwrState-Sts'
            self._pvs.append(_PV(VACA_PREFIX + dev + ppty))
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Check PS PwrState."""
        if not self._quit_task:
            for dev, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(dev)
                pv.get()  # force connection
                t = _time.time()
                is_ok = False
                if pv.connected:
                    while _time.time() - t < TIMEOUT_CHECK:
                        if pv.get() == self._state:
                            is_ok = True
                            break
                        if self._quit_task:
                            break
                self.itemDone.emit(dev, is_ok)
                _time.sleep(TIMEOUT_SLEEP)
                if self._quit_task:
                    break
        self.completed.emit()


class SetCtrlLoop(QThread):
    """Set PS CtrlLoop."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices_2_defvals, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices_2_defvals = devices_2_defvals
        self._pvs = {dev: _PV(VACA_PREFIX + dev + ':CtrlLoop-Sel')
                     for dev in devices_2_defvals.keys()}
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS CtrlLoop."""
        if not self._quit_task:
            for dev, pv in self._pvs.items():
                self.currentItem.emit(dev)
                pv.get()  # force connection
                if pv.connected:
                    pv.put(self._devices_2_defvals[dev][0])
                    _time.sleep(TIMEOUT_SLEEP)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()


class CheckCtrlLoop(QThread):
    """Check PS CtrlLoop."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices_2_defvals, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices_2_defvals = devices_2_defvals
        self._pvs = {dev: _PV(VACA_PREFIX + dev + ':CtrlLoop-Sts')
                     for dev in devices_2_defvals.keys()}
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Check PS CtrlLoop."""
        if not self._quit_task:
            for dev, pv in self._pvs.items():
                self.currentItem.emit(dev)
                pv.get()  # force connection
                t = _time.time()
                is_ok = False
                if pv.connected:
                    while _time.time() - t < TIMEOUT_CHECK:
                        defval = self._devices_2_defvals[dev][0]
                        if pv.get() == defval:
                            is_ok = True
                            break
                        if self._quit_task:
                            break
                self.itemDone.emit(dev, is_ok)
                _time.sleep(TIMEOUT_SLEEP)
                if self._quit_task:
                    break
        self.completed.emit()


class SetCapBankVolt(QThread):
    """Set current value and check if it RB is achieved."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices_2_defvals, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._quit_task = False
        self._devices_2_defvals = devices_2_defvals
        self._sp_pvs = dict()
        self._mon_pvs = dict()
        for dev in devices_2_defvals.keys():
            self._sp_pvs[dev] = \
                _PV(VACA_PREFIX + dev + ':CapacitorBankVoltage-SP')
            self._mon_pvs[dev] = \
                _PV(VACA_PREFIX + dev + ':CapacitorBankVoltage-Mon')

    def size(self):
        """Task size."""
        return len(self._devices_2_defvals.keys())

    def exit_task(self):
        """Exit flag."""
        self._quit_task = True

    def run(self):
        """Set PS Current."""
        if not self._quit_task:
            for dev, defval in self._devices_2_defvals.items():
                self.currentItem.emit(dev)

                sp = self._sp_pvs[dev]
                sp.get()  # force connection
                mon = self._mon_pvs[dev]
                mon.get()  # force connection

                if not mon.connected or not sp.connected:
                    self.itemDone.emit(dev, False)
                else:
                    sp.put(defval[1])
                    if defval != DEFAULT_CAP_BANK_VOLT['Default']:
                        success = False
                        t = _time.time()
                        while _time.time() - t < 6*TIMEOUT_CHECK:
                            if self._cmp(mon.get(), defval[1]):
                                success = True
                                break
                            if self._quit_task:
                                break
                    else:
                        success = True
                    self.itemDone.emit(dev, success)
                if self._quit_task:
                    break
        self.completed.emit()

    def _cmp(self, value, target):
        if value > target:
            return True
        else:
            return False


class SetCurrent(QThread):
    """Set current value and check if it RB is achieved."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, is_test=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._quit_task = False
        self._is_test = is_test
        self._devices = devices
        self._sp_pvs = list()
        self._mon_pvs = list()
        for dev in devices:
            sp_ppty = ':seti' if 'LI' in dev else ':Current-SP'
            self._sp_pvs.append(_PV(VACA_PREFIX + dev + sp_ppty))
            mon_ppty = ':rdi' if 'LI' in dev else ':Current-Mon'
            self._mon_pvs.append(_PV(VACA_PREFIX + dev + mon_ppty))

    def size(self):
        """Task size."""
        return len(self._devices)

    def exit_task(self):
        """Exit flag."""
        self._quit_task = True

    def run(self):
        """Set PS Current."""
        if not self._quit_task:
            for i in range(len(self._devices)):
                dev_name = self._devices[i]
                self.currentItem.emit(dev_name)

                sp = self._sp_pvs[i]
                sp.get()  # force connection
                mon = self._mon_pvs[i]
                mon.get()  # force connection

                if not mon.connected or not sp.connected:
                    self.itemDone.emit(dev_name, False)
                else:
                    if self._is_test:
                        if 'LI' in dev_name:
                            splims = PSSearch.conv_pstype_2_splims(
                                PSSearch.conv_psname_2_pstype(dev_name))
                        else:
                            splims = MASearch.conv_maname_2_splims(dev_name)
                        sp_val = splims['HIGH']/2.0
                    else:
                        sp_val = 0.0
                    sp.put(sp_val)
                    success = False

                    t = _time.time()
                    while _time.time() - t < TIMEOUT_CHECK:
                        if self._cmp(mon.get(), sp_val):
                            success = True
                            break
                        if self._quit_task:
                            break
                    self.itemDone.emit(dev_name, success)
                if self._quit_task:
                    break
        self.completed.emit()

    def _cmp(self, value, target, error=TEST_TOLERANCE):
        if abs(value - target) < error:
            return True
        else:
            return False
