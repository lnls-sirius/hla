"""Booster Ramp Control HLA: General Status Module."""

from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, \
                           QSizePolicy as QSzPlcy, QSpacerItem, \
                           QFormLayout, QHBoxLayout, QGridLayout
from qtpy.QtCore import Qt, Slot
from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming, ConnSOFB as _ConnSOFB
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriushla.widgets import PyDMLedMultiChannel, PyDMLedMultiConnection
from siriushla.bo_ap_ramp.auxiliar_classes import MessageBox as _MessageBox

COMMANDS_TIMEOUT = 1


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('General Status and Commands', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._manames = ramp.BoosterNormalized().manames
        self._conn_ma = _ConnMagnets(prefix=self.prefix)
        self._conn_ti = _ConnTiming(prefix=self.prefix)
        self._conn_rf = _ConnRF(prefix=self.prefix)
        self._conn_sofb = _ConnSOFB(prefix=self.prefix)
        self._setupUi()

    def _setupUi(self):
        status_layout = self._setupStatusLayout()
        commands_layout = self._setupCommandsLayout()

        glay = QGridLayout()
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        glay.addLayout(status_layout, 1, 1, 1, 3)
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 1)
        glay.addLayout(commands_layout, 3, 2)
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 4)
        self.setLayout(glay)

    def _setupStatusLayout(self):
        label_timing = QLabel('<h4>TI</h4>', self, alignment=Qt.AlignCenter)
        label_timing.setFixedSize(80, 40)
        label_magnets = QLabel('<h4>MA</h4>', self, alignment=Qt.AlignCenter)
        label_magnets.setFixedSize(80, 40)
        label_rf = QLabel('<h4>RF</h4>', self, alignment=Qt.AlignCenter)
        label_rf.setFixedSize(80, 40)
        label_sofb = QLabel('<h4>SOFB</h4>', self, alignment=Qt.AlignCenter)
        label_sofb.setFixedSize(80, 40)
        label_conn = QLabel('Connection', self)
        label_ramping = QLabel('Configured to Ramp', self)
        label_intlks = QLabel('Interlocks', self)
        label_rmprdy = QLabel('Ramp Ready', self)

        for led_name in ['led_ti_conn', 'led_ma_conn', 'led_rf_conn',
                         'led_sofb_conn']:
            channels = list()
            conn = getattr(
                self, led_name.replace('_conn', '').replace('led', '_conn'))
            for prpty in conn.properties:
                if 'ma' in led_name:
                    if 'PwrState' in conn[prpty].name:
                        channels.append(self.prefix + conn[prpty].pvname_rb)
                else:
                    channels.append(self.prefix + conn[prpty].pvname_rb)
            setattr(self, led_name, PyDMLedMultiConnection(self, channels))
            led = getattr(self, led_name)
            led.setFixedSize(80, 40)

        for led_name in ['led_ti_ramping', 'led_ma_ramping', 'led_rf_ramping',
                         'led_ma_intlk', 'led_rf_intlk',
                         'led_ma_rmprdy', 'led_rf_rmprdy']:
            channels2values = dict()
            conn = getattr(self, led_name[0:6].replace('led', '_conn'))
            if 'ti' in led_name:
                c = self._conn_ti.Const
                channels2values[c.EVG_Evt01Mode + '-Sts'] = c.MODE_CONTINUOUS
                channels2values[c.EVG_ContinuousEvt + '-Sts'] = c.STATE_ENBL
                self.update_wfmnrpoints()
            elif 'ma' in led_name:
                for prpty in conn.properties:
                    value = None
                    if 'ramping' in led_name:
                        if 'OpMode' in conn[prpty].name:
                            value = _PSConst.OpMode.RmpWfm
                    elif 'intlk' in led_name:
                        if 'PwrState' in conn[prpty].name:
                            value = _PSConst.PwrState.On
                        elif 'IntlkSoft' in conn[prpty].name:
                            value = 0
                        elif 'IntlkHard' in conn[prpty].name:
                            value = 0
                    elif 'rmprdy' in led_name:
                        if 'RmpReady' in conn[prpty].name:
                            value = 1
                    if value is None:
                        continue
                    channels2values[self.prefix+conn[prpty].pvname_rb] = value
            else:
                c = self._conn_rf.Const
                if 'ramping' in led_name:
                    self.update_rfparams()
                elif 'intlk' in led_name:
                    channels2values[self.prefix + c.Rmp_Intlk + '-Mon'] = 0
                elif 'rmprdy' in led_name:
                    channels2values[self.prefix + c.Rmp_RmpReady + '-Mon'] = 1

            setattr(self, led_name, PyDMLedMultiChannel(self, channels2values))
            led = getattr(self, led_name)
            led.setFixedSize(80, 40)

        flay = QFormLayout()
        flay.setLabelAlignment(Qt.AlignLeft)
        flay.setFormAlignment(Qt.AlignCenter)
        flay.setHorizontalSpacing(10)
        hlay = QHBoxLayout()
        hlay.addWidget(label_magnets)
        hlay.addWidget(label_rf)
        hlay.addWidget(label_timing)
        hlay.addWidget(label_sofb)
        flay.addRow(QLabel(''), hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_ma_conn)
        hlay.addWidget(self.led_rf_conn)
        hlay.addWidget(self.led_ti_conn)
        hlay.addWidget(self.led_sofb_conn)
        flay.addRow(label_conn, hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_ma_ramping)
        hlay.addWidget(self.led_rf_ramping)
        hlay.addWidget(self.led_ti_ramping)
        flay.addRow(label_ramping, hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_ma_intlk)
        hlay.addWidget(self.led_rf_intlk)
        flay.addRow(label_intlks, hlay)
        hlay = QHBoxLayout()
        hlay.addWidget(self.led_ma_rmprdy)
        hlay.addWidget(self.led_rf_rmprdy)
        flay.addRow(label_rmprdy, hlay)
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

        self.bt_setup.clicked.connect(self._setup_ramp)
        self.bt_apply_ps.clicked.connect(self._apply_ps)
        self.bt_apply_rf.clicked.connect(self._apply_rf)
        self.bt_apply_all.clicked.connect(self._apply_all)
        self.bt_start_ramp.clicked.connect(self._start_ramp)
        self.bt_stop_ramp.clicked.connect(self._stop_ramp)
        self.bt_start_inj.clicked.connect(self._start_inj)
        self.bt_stop_inj.clicked.connect(self._stop_inj)

        for bt in ['bt_setup', 'bt_apply_ps', 'bt_apply_rf',
                   'bt_apply_all', 'bt_start_ramp', 'bt_stop_ramp',
                   'bt_start_inj', 'bt_stop_inj']:
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
        return flay

    def _setup_ramp(self):
        if not self._verify_connector(self._conn_ma):
            return
        if not self._verify_connector(self._conn_ti):
            return

        configured_MA = self._conn_ma.cmd_opmode_rmpwfm(COMMANDS_TIMEOUT)
        if not configured_MA:
            warn_msg = _MessageBox(
                self, 'Failed to set OpMode',
                'Command failed to set all PS\nOpMode to RmpWfm!', 'Ok')
            warn_msg.exec_()
            return

        configured_TI = self._conn_ti.cmd_init()
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\nto ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_ps(self):
        if not self._verify_connector(self._conn_ma):
            return
        if not self._verify_connector(self._conn_ti):
            return

        uploaded = self._conn_ma.cmd_wfmdata(COMMANDS_TIMEOUT)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to set all PS\nwaveforms!', 'Ok')
            warn_msg.exec_()
            return

        # TODO: change to config only wfm_nrpoints+duration dependences
        uploaded = self._conn_ti.cmd_select_ramp(COMMANDS_TIMEOUT)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to configure timing\nto ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_rf(self):
        if not self._verify_connector(self._conn_rf):
            return

        uploaded = self._conn_rf.cmd_config_ramp(COMMANDS_TIMEOUT)
        if not uploaded:
            warn_msg = _MessageBox(
                self, 'Failed to Upload',
                'Command failed to set RF\nparameters!', 'Ok')
            warn_msg.exec_()
            return

    def _apply_all(self):
        self._apply_ps()
        self._apply_rf()

    def _start_ramp(self):
        """Start ramp.

        This action starts only timing pulses and RF ramp increase.
        Power supplies and RF need to be configured to ramp.
        """
        if not self._verify_connector(self._conn_ti):
            return
        if not self._verify_connector(self._conn_rf):
            return

        # TODO: verify timing control of this button
        configured_TI = self._conn_ti.cmd_select_ramp(COMMANDS_TIMEOUT)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to initialize pulses to ramp!', 'Ok')
            warn_msg.exec_()
            return

        configured_RF = self._conn_rf.cmd_ramping_enable(COMMANDS_TIMEOUT)
        if not configured_RF:
            warn_msg = _MessageBox(
                self, 'Failed to enable RF ramping',
                'Command failed to configure RF\n'
                'to start ramp increase to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _stop_ramp(self):
        """Stop ramp.

        This action stops only timing pulses.
        Power supplies and RF devices continue configured to ramp.
        """
        if not self._verify_connector(self._conn_ti):
            return

        configured_TI = self._conn_ti.cmd_select_stop(COMMANDS_TIMEOUT)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure PS and RF\n'
                'timing parameters!', 'Ok')
            warn_msg.exec_()
            return

        self._conn_ti.wait_EVRs()

    def _start_inj(self):
        if not self._verify_connector(self._conn_ti):
            return

        # TODO: change to control injection, not ramp
        configured_TI = self._conn_ti.cmd_select_ramp(COMMANDS_TIMEOUT)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to ramp!', 'Ok')
            warn_msg.exec_()
            return

    def _stop_inj(self):
        if not self._verify_connector(self._conn_ti):
            return

        # TODO: change to control injection, not ramp
        configured_TI = self._conn_ti.cmd_select_stop(COMMANDS_TIMEOUT)
        if not configured_TI:
            warn_msg = _MessageBox(
                self, 'Failed to Configure Timing',
                'Command failed to configure timing\n'
                'to stop pulsing!', 'Ok')
            warn_msg.exec_()
            return

    def _verify_connector(self, connector):
        if not connector:
            return False
        if not connector.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected', 'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return False
        return True

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Receive connectors."""
        self.ramp_config = ramp_config
        self._conn_ma.get_ramp_config(self.ramp_config)
        self._conn_ti.get_ramp_config(self.ramp_config)
        self._conn_rf.get_ramp_config(self.ramp_config)
        self.update_wfmnrpoints()
        self.update_rfparams()

    def update_wfmnrpoints(self):
        """Update waveform number of points in connector check values."""
        if self.ramp_config:
            c = self._conn_ti.Const
            self.led_ti_ramping.channels2values[c.EVR1_OTP08Pulses+'-RB'] = \
                self.ramp_config.ps_ramp_wfm_nrpoints

    def update_rfparams(self):
        """Update rf parameters in connector check values."""
        if self.ramp_config:
            c = self._conn_rf.Const
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_Ts1 + '-RB'] = \
                self.ramp_config.rf_ramp_bottom_duration
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_Ts2 + '-RB'] = \
                self.ramp_config.rf_ramp_rampup_duration
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_Ts3 + '-RB'] = \
                self.ramp_config.rf_ramp_top_duration
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_Ts4 + '-RB'] = \
                self.ramp_config.rf_ramp_rampdown_duration
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_IncTs + '-RB'] = \
                self.ramp_config.rf_ramp_rampinc_duration
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_VoltBot + '-RB'] = \
                self.ramp_config.rf_ramp_bottom_voltage
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_VoltTop + '-RB'] = \
                self.ramp_config.rf_ramp_top_voltage
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_PhsBot + '-RB'] = \
                self.ramp_config.rf_ramp_bottom_phase
            self.led_rf_ramping.channels2values[
                self.prefix + c.Rmp_PhsTop + '-RB'] = \
                self.ramp_config.rf_ramp_top_phase
