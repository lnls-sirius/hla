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
            for pvn in self._pvnames:
                self.currentItem.emit(pvn)
                value = self.get_pv(pvn).get(self._timeout)
                if value is not None:
                    self.itemRead.emit(pvn, QVariant(value))
                else:
                    self.itemNotRead.emit(pvn)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
