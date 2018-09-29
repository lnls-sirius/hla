"""Booster Ramp Control HLA: General Status Module."""

from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, \
                           QSizePolicy as QSzPlcy, QSpacerItem, \
                           QFormLayout, QHBoxLayout, QGridLayout
from qtpy.QtGui import QColor
from qtpy.QtCore import Qt, Slot
from siriushla.widgets import QLed
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming, \
                               ConnRF as _ConnRF
from siriushla.bo_ap_ramp.auxiliar_classes import MessageBox as _MessageBox

DarkGreen = QColor(20, 80, 10)


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('General Status and Commands', parent)
        self.prefix = prefix
        self._conn_magnets = None
        self._conn_timing = None
        self._conn_rf = None
        self._setupUi()

    def _setupUi(self):
        status_layout = self._setupStatusLayout()
        commands_layout = self._setupCommandsLayout()

        self.setLayout(QGridLayout())
        self.layout().addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        self.layout().addLayout(status_layout, 1, 1, 1, 3)
        self.layout().addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 2, 1)
        self.layout().addLayout(commands_layout, 3, 2)
        self.layout().addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 4)

    def _setupStatusLayout(self):
        label_timing = QLabel('<h4>TI</h4>', self, alignment=Qt.AlignCenter)
        label_timing.setFixedSize(60, 40)
        label_magnets = QLabel('<h4>MA</h4>', self, alignment=Qt.AlignCenter)
        label_magnets.setFixedSize(60, 40)
        label_rf = QLabel('<h4>RF</h4>', self, alignment=Qt.AlignCenter)
        label_rf.setFixedSize(60, 40)
        label_conn = QLabel('Connection', self)
        label_ramping = QLabel('Configured to Ramp', self)

        for led_name in ['led_conntiming', 'led_ti_ramping',
                         'led_connmagnets', 'led_ma_ramping',
                         'led_connrf', 'led_rf_ramping']:
            setattr(self, led_name, QLed(self))
            led = getattr(self, led_name)
            led.setOffColor(DarkGreen)
            led.state = False
            led.setFixedSize(60, 40)

        flay = QFormLayout()
        flay.setLabelAlignment(Qt.AlignLeft)
        flay.setFormAlignment(Qt.AlignCenter)
        flay.setHorizontalSpacing(10)
        hlay = QHBoxLayout()
        hlay.addWidget(label_timing)
        hlay.addWidget(label_magnets)
        hlay.addWidget(label_rf)
        flay.addRow(QLabel(''), hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_conntiming)
        hlay.addWidget(self.led_connmagnets)
        hlay.addWidget(self.led_connrf)
        flay.addRow(label_conn, hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_ti_ramping)
        hlay.addWidget(self.led_ma_ramping)
        hlay.addWidget(self.led_rf_ramping)
        flay.addRow(label_ramping, hlay)
        return flay

    def _setupCommandsLayout(self):
        self.bt_setup = QPushButton('Setup subsystems to ramp', self)

        label_apply = QLabel('Apply to: ', self,
                             alignment=Qt.AlignCenter)
        self.bt_apply_ps = QPushButton('PS', self)
        self.bt_apply_rf = QPushButton('RF', self)
        self.bt_apply_all = QPushButton('All', self)

        label_ramping = QLabel('Ramping: ', self, alignment=Qt.AlignCenter)
        self.bt_start_ramp = QPushButton('Start', self)
        self.bt_stop_ramp = QPushButton('Stop', self)

        label_injection = QLabel('Injection: ', self, alignment=Qt.AlignCenter)
        self.bt_start_inj = QPushButton('Start', self)
        self.bt_stop_inj = QPushButton('Stop', self)

        self.bt_cycle_ps = QPushButton('Cycling PS window', self)

        self.bt_setup.clicked.connect(self._setup_ramp)
        self.bt_apply_ps.clicked.connect(self._apply_ps)
        self.bt_apply_rf.clicked.connect(self._apply_rf)
        self.bt_apply_all.clicked.connect(self._apply_all)
        self.bt_start_ramp.clicked.connect(self._start_ramp)
        self.bt_stop_ramp.clicked.connect(self._stop_ramp)
        self.bt_start_inj.clicked.connect(self._start_inj)
        self.bt_stop_inj.clicked.connect(self._stop_inj)
        self.bt_cycle_ps.clicked.connect(self._openCyclePSWindow)

        for bt in ['bt_setup', 'bt_apply_ps', 'bt_apply_rf',
                   'bt_apply_all', 'bt_start_ramp', 'bt_stop_ramp',
                   'bt_start_inj', 'bt_stop_inj', 'bt_cycle_ps']:
            w = getattr(self, bt)
            w.setFixedHeight(48)
            if 'apply' in bt:
                w.setMaximumWidth(100)
            elif 'ramp' in bt or 'inj' in bt:
                w.setMaximumWidth(155)
            else:
                w.setMaximumWidth(440)

        flay = QFormLayout()
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)
        flay.addRow(self.bt_setup)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hbox = QHBoxLayout()
        hbox.addWidget(self.bt_apply_ps)
        hbox.addWidget(self.bt_apply_rf)
        hbox.addWidget(self.bt_apply_all)
        flay.addRow(label_apply, hbox)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hbox = QHBoxLayout()
        hbox.addWidget(self.bt_start_ramp)
        hbox.addWidget(self.bt_stop_ramp)
        flay.addRow(label_ramping, hbox)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hbox = QHBoxLayout()
        hbox.addWidget(self.bt_start_inj)
        hbox.addWidget(self.bt_stop_inj)
        flay.addRow(label_injection, hbox)
        flay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        flay.addRow(self.bt_cycle_ps)
        return flay

    def _openCyclePSWindow(self):
        # TODO: call cycle window
        pass

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

    def updateMAConnState(self):
        """Update magnets connection state led."""
        self.led_connmagnets.state = self._conn_magnets.connected

    def updateTIConnState(self):
        """Update timing connection state led."""
        self.led_conntiming.state = self._conn_timing.connected

    def updateRFConnState(self):
        """Update RF connection state led."""
        self.led_connrf.state = self._conn_rf.connected

    def updateMAOpModeState(self):
        """Update magnets operational mode state led."""
        self.led_ma_ramping.state = self._conn_magnets.check_opmode_rmpwfm()

    def updateTIOpModeState(self):
        """Update timing operational mode state led."""
        self.label_ti_ramping.state = self._conn_timing.check_ramp()

    def updateRFOpModeState(self):
        """Update RF operational mode state led."""
        self.label_rf_ramping.state = self._conn_rf.check_ramp()

    @Slot(_ConnMagnets, _ConnTiming, _ConnRF)
    def getConnectors(self, conn_magnet, conn_timing, conn_rf):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
        self._conn_rf = conn_rf
