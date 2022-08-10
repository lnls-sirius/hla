"""Monitor module of the Application Interface."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QWidget
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .chart import ChartWindow
from .controls import DEVICES, ControlBox


class LLRFMonitor(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.device = 'LA-RF:LLRF:'
        self.setObjectName('LIApp')
        self.setWindowTitle('LI LLRF')
        self.relative_widgets = []
        self._setupui()

    def _setupui(self):
        lay1 = QGridLayout()
        self.setLayout(lay1)

        for dev in DEVICES:
            grbox = QGroupBox(dev.label, self)
            lay = QGridLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            grbox.setLayout(lay)
            lay.addWidget(
                ControlBox(
                    grbox, dev.pvname, main_dev=self.device,
                    device=dev, prefix=self.prefix),
                0, 0)
            lay.addWidget(
                ChartWindow(
                    parent=self, dev=dev.pvname,
                    chart_type='Mon', channel='CH1'),
                0, 1)
            lay1.addWidget(grbox, dev.value, 0)
