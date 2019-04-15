"""EpicsTask interface."""
from qtpy.QtCore import QThread, Signal


class EpicsTask(QThread):
    """Interface to execute some task.

    Allows a QThread to work with ProgressDialog widget.
    Implements:
    currentItem (Signal)
    itemDone (Signal)
    size (method)
    exit_task (method)
    """

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, pvs, values, delays, cls_epics, parent=None):
        """Constructor.

        Parameters
        ----------
        pv_list - a list of PVs
        cls_epics - epics class that implements interface (put, get, check)
        values - values associated with the PVs [optional]
        parent - parent QObject [optional]
        """
        super().__init__(parent)
        self._pvs = [cls_epics(pv) for pv in pvs]
        self._values = values
        self._delays = delays
        self._quit_task = False

    def size(self):
        """Task Size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to exit thread."""
        self._quit_task = True
