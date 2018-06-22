"""Booster Ramp Control HLA: Ramp Commands Module."""

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from siriuspy.namesys import SiriusPVName as _PVName


class RampCommands(QGroupBox):
    """Widget to perform ramp commands related to epics."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Commands', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        self.bt_upload = QPushButton('Upload to PS', self)
        self.bt_cycle = QPushButton('Cycle', self)
        self.bt_start = QPushButton('Start', self)
        self.bt_stop = QPushButton('Stop', self)
        self.bt_abort = QPushButton('Abort', self)
        self.bt_abort.setStyleSheet('background-color: red;')

        self.bt_upload.clicked.connect(self._upload)
        self.bt_cycle.clicked.connect(self._cycle)
        self.bt_start.clicked.connect(self._start)
        self.bt_stop.clicked.connect(self._stop)
        self.bt_abort.clicked.connect(self._abort)

        lay = QVBoxLayout(self)
        lay.addWidget(self.bt_upload)
        lay.addWidget(self.bt_cycle)
        lay.addWidget(self.bt_start)
        lay.addWidget(self.bt_stop)
        lay.addWidget(self.bt_abort)

    def _calculate(self):
        print('Do stuff')

    def _upload(self):
        print('Do stuff')

    def _cycle(self):
        print('Do stuff')

    def _start(self):
        print('Do stuff')

    def _stop(self):
        print('Do stuff')

    def _abort(self):
        print('Do stuff')
