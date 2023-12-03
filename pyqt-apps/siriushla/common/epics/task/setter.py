"""Epics Setter."""
import time
import logging as _log
from epics.ca import ChannelAccessGetFailure as _ChannelAccessGetFailure, \
    CASeverityException as _CASeverityException
from .task import EpicsTask


class EpicsSetter(EpicsTask):
    """Set the value of a set of PVs."""

    def run(self):
        """Thread execution."""
        if not self._quit_task:
            for i, pvn in enumerate(self._pvnames):
                self.currentItem.emit(pvn)
                pv = self.get_pv(pvn)
                try:
                    pv.put(self._values[i])
                    time.sleep(self._delays[i])
                except (TypeError, _ChannelAccessGetFailure, _CASeverityException):
                    _log.warning('PV {} not set with value: {}'.format(
                        pvn, self._values[i]))
                self.itemDone.emit()
                if self._quit_task:
                    break
        self.completed.emit()
