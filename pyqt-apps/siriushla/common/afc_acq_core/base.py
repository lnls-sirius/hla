"""Base."""

from qtpy.QtWidgets import QWidget

from siriuspy.namesys import SiriusPVName as _PVName


class BaseWidget(QWidget):

    def __init__(
            self, parent=None, prefix='', device='', database=dict()):
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.sec = self.device.sec if self.device.sec != 'IA' else 'SI'
        self.setObjectName(self.sec+'App')
        self._db = database

    def get_pvname(self, propty):
        addr = self.device.substitute(
            prefix=self.prefix, propty=propty)
        return addr
