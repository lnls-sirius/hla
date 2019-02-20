"""Epics Getter."""
from .task import EpicsTask
from qtpy.QtCore import Signal, QVariant

class EpicsGetter(EpicsTask):
    """Get value of a set of PVs."""

    itemRead = Signal(str, QVariant)
    itemNotRead = Signal(str)

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.finished.emit()
        else:
            for i in range(len(self._pvs)):
                pv = self._pvs[i]
                self.currentItem.emit(pv.pvname)
                value = pv.get()
                self.itemDone.emit()
                if value is not None:
                    self.itemRead.emit(pv.pvname, QVariant(value))
                else:
                    self.itemNotRead.emit(pv.pvname)
                # self.itemRead(pv.pvname)
                if self._quit_task:
                    break
            self.finished.emit()
