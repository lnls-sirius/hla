"""Definition of a task interface."""
import time
from qtpy.QtCore import QThread, Signal, QVariant


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

    def __init__(self, pv_list, cls_epics, values=None, parent=None):
        """Constructor.

        Parameters
        ----------
        pv_list - a list of PVs
        cls_epics - epics class that implements interface (put, get, check)
        values - values associated with the PVs [optional]
        parent - parent QObject [optional]
        """
        super().__init__(parent)
        self._pvs = [cls_epics(pv) for pv in pv_list]
        self._values = values or list()
        self._quit_task = False

    def size(self):
        """Task Size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to exit thread."""
        self._quit_task = True


class EpicsSetter(EpicsTask):
    """Set the value of a set of PVs."""

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.finished.emit()
        else:
            for i in range(len(self._pvs)):
                self.currentItem.emit(self._pvs[i].pvname)
                self._pvs[i].put(self._values[i])
                self.itemDone.emit()
                if self._quit_task:
                    break
            self.finished.emit()


class EpicsChecker(EpicsTask):
    """Check if a set of PVs has the proper values."""

    itemChecked = Signal(str, bool)

    def run(self):
        """Thread execution."""
        if self._quit_task:
            self.finished.emit()
        else:
            time.sleep(3)
            for i in range(len(self._pvs)):
                pv, val = self._pvs[i], self._values[i]
                self.currentItem.emit(pv.pvname)
                equal = pv.check(val)
                self.itemDone.emit()
                self.itemChecked.emit(pv.pvname, equal)
                if self._quit_task:
                    break
            self.finished.emit()


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
