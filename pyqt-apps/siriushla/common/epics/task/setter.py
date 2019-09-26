"""Epics Setter."""
import time
import logging as _log
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
                except TypeError:
                    _log.warning('PV {} not set with value: {}'.format(
                        self._pvs[i].pvname, self._values[i]))
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
