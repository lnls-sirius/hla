import time as _time
from epics import PV as _PV

from qtpy.QtCore import Signal, QThread

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.csdevice.pwrsupply import Const as _PSC
from siriuspy.magnet.data import MAData


TIMEOUT_CHECK = 8
TIMEOUT_SLEEP = 0.1
TEST_TOLERANCE = 1e-3


class ResetIntlk(QThread):
    """Reset."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = [_PV(VACA_PREFIX + device + ':Reset-Cmd')
                     for device in devices]
        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._devices)

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        """Execute task."""
        if not self._quit_task:
            for device, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(device)
                pv.get()  # force connection
                if pv.connected:
                    pv.put(1)
                    _time.sleep(TIMEOUT_SLEEP)
                self.itemDone.emit()
        self.completed.emit()


class CheckIntlk(QThread):
    """Check if PS is on."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = list()
        for device in devices:
            self._pvs.append(_PV(VACA_PREFIX+device+':IntlkHard-Mon'))
            self._pvs.append(_PV(VACA_PREFIX+device+':IntlkSoft-Mon'))
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
            for device, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(device)
                t = _time.time()
                is_ok = False
                pv.get()  # force connection
                if pv.connected:
                    while _time.time() - t < TIMEOUT_CHECK:
                        if pv.value == 0:
                            is_ok = True
                            break
                        if self._quit_task:
                            break
                else:
                    print(pv.pvname, 'not conn')
                self.itemDone.emit(device, is_ok)
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
        self._pvs = [_PV(VACA_PREFIX + device + ':PwrState-Sel')
                     for device in devices]
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
            for device, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(device)
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
        self._pvs = [_PV(VACA_PREFIX + device + ':PwrState-Sts')
                     for device in devices]
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
            for device, pv in zip(self._devices, self._pvs):
                self.currentItem.emit(device)
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
                self.itemDone.emit(device, is_ok)
                _time.sleep(TIMEOUT_SLEEP)
                if self._quit_task:
                    break
        self.completed.emit()


class SetCurrent(QThread):
    """Set value and check if it rb is achieved."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, devices, is_test=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._quit_task = False
        self._is_test = is_test
        self._devices = devices
        self._sp_pvs = [_PV(VACA_PREFIX + device + ':Current-SP')
                        for device in devices]
        self._rb_pvs = [_PV(VACA_PREFIX + device + ':Current-RB')
                        for device in devices]

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

                rb = self._rb_pvs[i]
                rb.get()  # force connection
                sp = self._sp_pvs[i]
                sp.get()  # force connection

                if not rb.connected or not sp.connected:
                    self.itemDone.emit(dev_name, False)
                else:
                    if self._is_test:
                        splims = MAData(dev_name).splims
                        sp_val = splims['HIGH']/2.0
                    else:
                        sp_val = 0.0
                    sp.put(sp_val)
                    success = False

                    t = _time.time()
                    while _time.time() - t < TIMEOUT_CHECK:
                        if self._cmp(rb.get(), sp_val):
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
