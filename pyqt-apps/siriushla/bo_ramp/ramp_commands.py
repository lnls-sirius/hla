"""Booster Ramp Control HLA: Ramp Commands Module."""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton, \
                            QSpacerItem, QSizePolicy as QSzPlcy
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
        self.bt_upload = QPushButton('Send waveforms to PS', self)
        self.bt_cycle = QPushButton('Cycle', self)
        self.bt_start = QPushButton('Start Ramp', self)
        self.bt_stop = QPushButton('Stop Ramp', self)

        self.bt_upload.clicked.connect(self._uploadToPS)
        self.bt_cycle.clicked.connect(self._cycle)
        self.bt_start.clicked.connect(self._start)
        self.bt_stop.clicked.connect(self._stop)

        lay = QGridLayout(self)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(self.bt_upload, 1, 1)
        lay.addWidget(self.bt_cycle, 1, 3)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 2)
        lay.addWidget(self.bt_start, 3, 1)
        lay.addWidget(self.bt_stop, 3, 3)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 4)

    def _uploadToPS(self):
        if not self._conn_magnets:
            return

        if not self._conn_magnets.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        timeout = 0.5
        uploaded = self._conn_magnets.cmd_wfmdata(timeout)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to set all PS\n'
                'waveforms!', 'Ok')
            warn_msg.exec_()
            return

    def _cycle(self):
        if not self._conn_magnets or not self._conn_timing:
            return

        if not self._conn_magnets.connected or not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        configured_MA = self._conn_magnets.cmd_opmode_cycle()
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to Cycle!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_select_cycle()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to cycle!', 'Ok')
            warn_msg.exec_()
            return

        pulse_TI = self._conn_timing.cmd_pulse()
        if not pulse_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Pulse Timing',
                'Command failed to pulse timing\n'
                'to cycle!', 'Ok')
            warn_msg.exec_()
            return

    def _start(self):
        if not self._conn_magnets or not self._conn_timing:
            return

        if not self._conn_magnets.connected or not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        configured_MA = self._conn_magnets.cmd_opmode_rmpwfm()
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to RampWfm!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_select_ramp()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _stop(self):
        if not self._conn_magnets or not self._conn_timing:
            return

        if not self._conn_magnets.connected or not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        configured_MA = self._conn_magnets.cmd_opmode_slowref()
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\n'
                'OpMode to SlowRef!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_select_stop()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to stop pulsing!', 'Ok')
            warn_msg.exec_()
            return

        self._conn_timing.wait_EVRs()

    @pyqtSlot(_ConnMagnets, _ConnTiming)
    def getConnectors(self, conn_magnet, conn_timing):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
