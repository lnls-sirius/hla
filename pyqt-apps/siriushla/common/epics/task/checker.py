"""Epics Checker Task."""
from .task import EpicsTask
from ..wrapper import PyEpicsWrapper
from qtpy.QtCore import Signal


class EpicsChecker(EpicsTask):
    """Check if a set of PVs has the proper values."""

    itemChecked = Signal(str, bool)

    def __init__(self, pvs, values, delays, cls_epics=PyEpicsWrapper,
                 parent=None, timeout=PyEpicsWrapper.TIMEOUT):
        super().__init__(pvs, values, delays, cls_epics, parent, timeout)

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i, pvn in enumerate(self._pvnames):
                self.currentItem.emit(pvn)
                pv = self.get_pv(pvn)
                val = self._values[i]
                equal = pv.check(val, wait=self._timeout)
                self.itemChecked.emit(pvn, equal)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
