"""Epics Checker Task."""
from .task import EpicsTask
from qtpy.QtCore import Signal

class EpicsChecker(EpicsTask):
    """Check if a set of PVs has the proper values."""

    itemChecked = Signal(str, bool)

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.finished.emit()
        else:
            for i in range(len(self._pvs)):
                pv, val = self._pvs[i], self._values[i]
                self.currentItem.emit(pv.pvname)
                equal = pv.check(val)
                self.itemDone.emit()
                self.itemChecked.emit(pv.pvname, equal)
                if self._quit_task:
                    break
            self.finished.emit()
