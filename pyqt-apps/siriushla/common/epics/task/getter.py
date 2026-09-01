"""Epics Getter."""
from qtpy.QtCore import Signal
from .task import EpicsTask
from ..wrapper import PyEpicsWrapper


class EpicsGetter(EpicsTask):
    """Get value of a set of PVs."""

    itemRead = Signal(str, object)
    itemNotRead = Signal(str)

    def __init__(self, pvs, defvals=None, cls_epics=PyEpicsWrapper,
                 parent=None, timeout=PyEpicsWrapper.TIMEOUT):
        super().__init__(pvs, defvals, None, cls_epics, parent, timeout)

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i, pvn in enumerate(self._pvnames):
                self.currentItem.emit(pvn)
                value = self.get_pv(pvn).get(self._timeout)
                if pvn.endswith('-Cmd') and self._values is not None:
                    self.itemRead.emit(pvn, self._values[i])
                elif value is not None:
                    self.itemRead.emit(pvn, value)
                else:
                    self.itemNotRead.emit(pvn)
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
