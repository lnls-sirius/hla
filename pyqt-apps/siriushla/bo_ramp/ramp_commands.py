"""Booster Ramp Control HLA: Ramp Commands Module."""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming
from siriushla.bo_ramp.auxiliar_classes import MessageBox as _MessageBox


class RampCommands(QGroupBox):
    """Widget to perform ramp commands related to epics."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('Commands', parent)
        self.prefix = _PVName(prefix)
        self._conn_magnets = None
        self._conn_timing = None
        self._setupUi()

    def _setupUi(self):
        self.setFixedHeight(500)

        self.bt_upload = QPushButton('Upload to PS', self)
        self.bt_cycle = QPushButton('Cycle', self)
        self.bt_start = QPushButton('Start Ramp', self)
        self.bt_stop = QPushButton('Stop Ramp', self)

        self.bt_upload.clicked.connect(self._uploadToPS)
        self.bt_cycle.clicked.connect(self._cycle)
        self.bt_start.clicked.connect(self._start)
        self.bt_stop.clicked.connect(self._stop)

        lay = QVBoxLayout(self)
        lay.addWidget(self.bt_upload)
        lay.addWidget(self.bt_cycle)
        lay.addWidget(self.bt_start)
        lay.addWidget(self.bt_stop)

    def _uploadToPS(self):
        if not self._conn_magnets:
            return
        timeout = 0.5
        uploaded = self._conn_magnets.cmd_wfmdata(timeout)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to set all PS\n'
                'waveforms with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

    def _initTiming(self):
        if not self._conn_timing:
            return
        timeout = 0.5
        configured_TI = self._conn_timing.cmd_init(timeout)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Failed to initialize timing\n'
                'with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return False
        return True

    def _cycle(self):
        if not self._conn_magnets or not self._conn_timing:
            return
        timeout = 0.5
        configured_MA = self._conn_magnets.cmd_opmode_cycle(timeout)
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to Cycle with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

        init = self._initTiming(timeout)
        if not init:
            return

        configured_TI = self._conn_timing.cmd_select_cycle(timeout)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to cycle with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

    def _start(self):
        if not self._conn_magnets or not self._conn_timing:
            return
        timeout = 0.5
        configured_MA = self._conn_magnets.cmd_opmode_rmpwfm(timeout)
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to RampWfm with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

        init = self._initTiming(timeout)
        if not init:
            return

        configured_TI = self._conn_timing.cmd_select_ramp(timeout)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to ramp with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

    def _stop(self):
        if not self._conn_magnets or not self._conn_timing:
            return
        timeout = 0.5
        configured_MA = self._conn_magnets.cmd_opmode_slowref(timeout)
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to RampWfm with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_select_stop(timeout)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to cycle with timeout {}!'.format(timeout), 'Ok')
            warn_msg.exec_()
            return

        self._conn_timing.wait_EVRs()

    @pyqtSlot(_ConnMagnets, _ConnTiming)
    def getConnectors(self, conn_magnet, conn_timing):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
