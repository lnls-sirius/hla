"""Epics Checker Task."""
from .task import EpicsTask
from qtpy.QtCore import Signal


class EpicsChecker(EpicsTask):
    """Check if a set of PVs has the proper values."""

    itemChecked = Signal(str, bool)

    def __init__(self, pvs, values, delays, cls_epics, parent=None,
                 timeout=10):
        super().__init__(pvs, values, delays, cls_epics, parent)
        self._timeout = timeout

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i in range(len(self._pvnames)):
                pv, val = EpicsTask.PVs[i], self._values[i]
                self.currentItem.emit(pv.pvname)
                equal = pv.check(val, wait=self._timeout)
                self.itemDone.emit()
                self.itemChecked.emit(pv.pvname, equal)
                if self._quit_task:
                    break
        self.completed.emit()
