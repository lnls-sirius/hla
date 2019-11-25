"""Epics Getter."""
from qtpy.QtCore import Signal, QVariant
from .task import EpicsTask
from ..wrapper import PyEpicsWrapper


class EpicsGetter(EpicsTask):
    """Get value of a set of PVs."""

    itemRead = Signal(str, QVariant)
    itemNotRead = Signal(str)

    def __init__(self, pvs, cls_epics=PyEpicsWrapper, parent=None,
                 timeout=PyEpicsWrapper.TIMEOUT):
        super().__init__(pvs, None, None, cls_epics, parent, timeout)

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i in range(len(self._pvnames)):
                pv = EpicsTask.PVs[i]
                self.currentItem.emit(pv.pvname)
                value = pv.get(self._timeout)
                self.itemDone.emit()
                if value is not None:
                    self.itemRead.emit(pv.pvname, QVariant(value))
                else:
                    self.itemNotRead.emit(pv.pvname)
                if self._quit_task:
                    break
        self.completed.emit()
