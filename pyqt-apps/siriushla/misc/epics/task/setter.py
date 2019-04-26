"""Epics Setter."""
import time
from .task import EpicsTask


class EpicsSetter(EpicsTask):
    """Set the value of a set of PVs."""

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.completed.emit()
        else:
            for i in range(len(self._pvs)):
                self.currentItem.emit(self._pvs[i].pvname)
                self._pvs[i].put(self._values[i])
                time.sleep(self._delays[i])
                self.itemDone.emit()
                if self._quit_task:
                    break
            self.completed.emit()
