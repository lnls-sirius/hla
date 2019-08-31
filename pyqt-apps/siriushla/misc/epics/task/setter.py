"""Epics Setter."""
import time
from .task import EpicsTask


class EpicsSetter(EpicsTask):
    """Set the value of a set of PVs."""

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i in range(len(self._pvs)):
                self.currentItem.emit(self._pvs[i].pvname)
                try:
                    self._pvs[i].put(self._values[i])
                    time.sleep(self._delays[i])
                except Exception:
                    print(
                        'PV ', self._pvs[i].pvname, 
                        ' not set wit value: ', self._values[i])
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
