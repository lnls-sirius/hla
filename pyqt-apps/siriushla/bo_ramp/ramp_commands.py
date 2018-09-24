"""Booster Ramp Control HLA: Ramp Commands Module."""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton, \
                            QSpacerItem, QSizePolicy as QSzPlcy
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming,\
                               ConnRF as _ConnRF
from siriushla.bo_ramp.auxiliar_classes import MessageBox as _MessageBox


class RampCommands(QGroupBox):
    """Widget to perform ramp commands related to epics."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('Commands', parent)
        self.prefix = _PVName(prefix)
        self._conn_magnets = None
        self._conn_timing = None
        self._conn_rf = None
        self._setupUi()

    def _setupUi(self):
        self.bt_cycle_ps = QPushButton('Cycle PS', self)
        self.bt_setup_ramp = QPushButton('Setup ramp', self)
        self.bt_apply_ps = QPushButton('Apply to PS', self)
        self.bt_apply_rf = QPushButton('Apply to RF', self)
        self.bt_apply_all = QPushButton('Apply to all', self)
        self.bt_start_ramp = QPushButton('Start Ramp', self)
        self.bt_stop_ramp = QPushButton('Stop Ramp', self)
        self.bt_start_inj = QPushButton('Start Injection', self)
        self.bt_stop_inj = QPushButton('Stop Injection', self)

        self.bt_cycle_ps.clicked.connect(self._cycle_ps)
        self.bt_setup_ramp.clicked.connect(self._setup_ramp)
        self.bt_apply_ps.clicked.connect(self._apply_ps)
        self.bt_apply_rf.clicked.connect(self._apply_rf)
        self.bt_apply_all.clicked.connect(self._apply_all)
        self.bt_start_ramp.clicked.connect(self._start_ramp)
        self.bt_stop_ramp.clicked.connect(self._stop_ramp)
        self.bt_start_inj.clicked.connect(self._start_inj)
        self.bt_stop_inj.clicked.connect(self._stop_inj)

        lay = QGridLayout(self)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(self.bt_cycle_ps, 1, 1, 1, 6)
        lay.addWidget(self.bt_setup_ramp, 2, 1, 1, 6)
        lay.addWidget(self.bt_apply_ps, 3, 1, 1, 2)
        lay.addWidget(self.bt_apply_rf, 3, 3, 1, 2)
        lay.addWidget(self.bt_apply_all, 3, 5, 1, 2)
        lay.addWidget(self.bt_start_ramp, 4, 1, 1, 3)
        lay.addWidget(self.bt_stop_ramp, 4, 4, 1, 3)
        lay.addWidget(self.bt_start_inj, 5, 1, 1, 3)
        lay.addWidget(self.bt_stop_inj, 5, 4, 1, 3)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 7)

    def _cycle_ps(self):
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

    def _setup_ramp(self):
        if not self._conn_magnets or not self._conn_timing \
                or not self._conn_rf:
            return

        if not self._conn_magnets.connected or \
                not self._conn_timing.connected or \
                not self._conn_rf.connected:
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
                'OpMode to RmpWfm!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_init()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

        configured_RF = self._conn_rf.cmd_ramping_enable()
        if not configured_RF:
            warn_msg = _MessageBox(
                self, 'Failed to Configure RF',
                'Command failed to configure RF\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_ps(self):
        if not self._conn_magnets or not self._conn_timing:
            return

        if not self._conn_magnets.connected or not self._conn_timing.connected:
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

        # TODO: change to config only wfm_nrpoints+duration dependences
        timeout = 0.5
        uploaded = self._conn_timing.cmd_select_ramp(timeout)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to configure timing\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_rf(self):
        if not self._conn_rf:
            return

        if not self._conn_rf.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        timeout = 0.5
        uploaded = self._conn_rf.cmd_config_ramp(timeout)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to set RF\n'
                'parameters!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_all(self):
        self._apply_ps()
        self._apply_rf()

    def _start_ramp(self):
        if not self._conn_magnets or not self._conn_timing:
            return

        if not self._conn_magnets.connected or not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_timing.cmd_select_ramp()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure PS and RF\n'
                'timing parameters!', 'Ok')
            warn_msg.exec_()
            return

    def _stop_ramp(self):
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
                'Command failed to configure PS and RF\n'
                'timing parameters!', 'Ok')
            warn_msg.exec_()
            return

        self._conn_timing.wait_EVRs()

    def _start_inj(self):
        if not self._conn_timing:
            return

        if not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        # TODO: change to control injection, not ramp
        configured_TI = self._conn_timing.cmd_select_ramp()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _stop_inj(self):
        if not self._conn_timing:
            return

        if not self._conn_timing.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return

        # TODO: change to control injection, not ramp
        configured_TI = self._conn_timing.cmd_select_stop()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to stop pulsing!', 'Ok')
            warn_msg.exec_()
            return

    @pyqtSlot(_ConnMagnets, _ConnTiming, _ConnRF)
    def getConnectors(self, conn_magnet, conn_timing, conn_rf):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
        self._conn_rf = conn_rf
