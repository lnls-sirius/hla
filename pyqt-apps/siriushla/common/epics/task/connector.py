"""Epics Connector."""
from .task import EpicsTask
from ..wrapper import PyEpicsWrapper


class EpicsConnector(EpicsTask):
    """Interface to execute some task.

    Allows a QThread to work with ProgressDialog widget.
    Implements:
    currentItem (Signal)
    itemDone (Signal)
    size (method)
    exit_task (method)
    """

    def __init__(self, pvs, cls_epics=PyEpicsWrapper, parent=None):
        super().__init__(pvs, None, None, cls_epics, parent)

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.completed.emit()
            return
        for pvn in self._pvnames:
            self.currentItem.emit(pvn)
            self.get_pv(pvn)
            self.itemDone.emit()
            if self._quit_task:
                break
        self.completed.emit()
