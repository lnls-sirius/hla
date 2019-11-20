"""Epics Getter."""
import logging as _log
from qtpy.QtCore import Signal, QVariant
from .task import EpicsTask


class EpicsConnector(EpicsTask):
    """Interface to execute some task.

    Allows a QThread to work with ProgressDialog widget.
    Implements:
    currentItem (Signal)
    itemDone (Signal)
    size (method)
    exit_task (method)
    """

    def __init__(self, values, cls_epics, parent=None):
        super().__init__(values, None, None, cls_epics, parent)

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.completed.emit()
            return
        EpicsTask.PVs = []
        for pvn in self._pvnames:
            self.currentItem.emit(pvn)
            EpicsTask.PVs.append(self._cls_epics(pvn))
            self.itemDone.emit()
            if self._quit_task:
                break
        self.completed.emit()
