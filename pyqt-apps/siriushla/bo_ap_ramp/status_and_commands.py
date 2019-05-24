"""Booster Ramp Control HLA: General Status Module."""

from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout
from qtpy.QtCore import Slot, Signal, QThread
from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming, ConnSOFB as _ConnSOFB
from siriuspy.csdevice.pwrsupply import Const as _PSc
from siriuspy.csdevice.timesys import Const as _TIc
from pydm.widgets import PyDMPushButton
from siriushla.widgets import PyDMLedMultiChannel, PyDMLedMultiConnection, \
                              SiriusLedState
from siriushla.bo_ap_ramp.auxiliar_classes import MessageBox as _MessageBox

COMMANDS_TIMEOUT = 1


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Controls', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._manames = ramp.BoosterNormalized().manames
        self._conn_ma = _ConnMagnets(prefix=self.prefix)
        self._conn_ti = _ConnTiming(prefix=self.prefix)
        self._conn_rf = _ConnRF(prefix=self.prefix)
        self._conn_sofb = _ConnSOFB(prefix=self.prefix)
        self._setupUi()

    def _setupUi(self):
        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(6)
        self.layout.setHorizontalSpacing(6)
        self.setLayout(self.layout)
        self._setupStatusLayout()
        self._setupCommandsLayout()

        self.setStyleSheet("""
            QLabel{
                qproperty-alignment: AlignCenter;
                min-height:1.55em; max-height:1.55em;}
            PyDMLedMultiChannel, PyDMLedMultiConnection{
                min-width:3em; max-width:3em;}""")

    def _setupStatusLayout(self):
        self.label_status = QLabel('<h4>Status</h4>', self)
        self.label_status.setStyleSheet("""
            qproperty-alignment: AlignBottom;
            min-height:1.55em; max-height:1.55em;""")

        pfx = self.prefix

        # Connection Leds
        for led_name in ['led_ma_conn', 'led_rf_conn', 'led_ti_conn',
                         'led_sofb_conn']:
            channels = list()
            conn = getattr(
                self, led_name.replace('_conn', '').replace('led', '_conn'))
            for p in conn.properties:
                if 'ma' in led_name:
                    if 'PwrState' in conn[p].name:
                        channels.append(pfx + conn[p].pvname_rb)
                else:
                    channels.append(pfx + conn[p].pvname_rb)
            setattr(self, led_name, PyDMLedMultiConnection(self, channels))

            label_name = led_name.replace('led', 'label').replace('_conn', '')
            text = '<h4>' + label_name.replace('label_', '').upper() + '</h4>'
            setattr(self, label_name, QLabel(text, self))

        # MA Leds
        conn = self._conn_ma
        c2v_intlk = dict()
        c2v_setup = dict()
        c2v_apply = dict()
        for p in conn.properties:
            if 'IntlkSoft' in conn[p].name or 'IntlkHard' in conn[p].name:
                c2v_intlk[pfx + conn[p].pvname_rb] = 0
            elif 'OpMode' in conn[p].name:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.OpMode.RmpWfm
            elif 'PwrState' in conn[p].name:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.PwrStateSel.On
            elif 'WfmData' in conn[p].name:
                c2v_apply[pfx + conn[p].pvname_rb] = None

        self.led_ma_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_ma_setup = PyDMLedMultiChannel(self, c2v_setup)
        self.led_ma_apply = PyDMLedMultiChannel(self, c2v_apply)

        # RF Leds
        conn = self._conn_rf
        c2v_intlk = {pfx + conn.Const.Rmp_Intlk: 0}
        c2v_apply = dict()
        c2v_apply[pfx + conn.Const.Rmp_Ts1.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts2.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts3.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts4.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_IncTs.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_VoltBot.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_VoltTop.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_PhsBot.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_PhsTop.replace('SP', 'RB')] = 0
        c2v_rmprdy = {pfx + conn.Const.Rmp_RmpReady: 1}

        self.led_rf_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_rf_rmprdy = PyDMLedMultiChannel(self, c2v_rmprdy)
        self.led_rf_apply = PyDMLedMultiChannel(self, c2v_apply)

        # TI Leds
        conn = self._conn_ti
        c2v_intlk = {pfx + conn.Const.Intlk: 0}
        c2v_basicsetup = dict()
        for prpty, value in conn.ramp_basicsetup.items():
            c2v_basicsetup[pfx + prpty] = value
        c2v_configsetup = dict()
        for prpty, value in conn.ramp_configsetup.items():
            c2v_configsetup[pfx + prpty] = value

        self.led_ti_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_ti_setup = PyDMLedMultiChannel(self, c2v_basicsetup)
        self.led_ti_apply = PyDMLedMultiChannel(self, c2v_configsetup)

        self.layout.addWidget(self.label_status, 0, 0, 1, 6)
        self.layout.addWidget(QLabel(''), 1, 0)
        self.layout.addWidget(self.label_ma, 1, 1)
        self.layout.addWidget(self.label_rf, 1, 2)
        self.layout.addWidget(self.label_ti, 1, 3)
        self.layout.addWidget(self.label_sofb, 1, 4)
        self.layout.addWidget(QLabel('Connection', self), 2, 0)
        self.layout.addWidget(self.led_ma_conn, 2, 1)
        self.layout.addWidget(self.led_rf_conn, 2, 2)
        self.layout.addWidget(self.led_ti_conn, 2, 3)
        self.layout.addWidget(self.led_sofb_conn, 2, 4)
        self.layout.addWidget(QLabel('Interlocks', self), 3, 0)
        self.layout.addWidget(self.led_ma_intlk, 3, 1)
        self.layout.addWidget(self.led_rf_intlk, 3, 2)
        self.layout.addWidget(self.led_ti_intlk, 3, 3)
        self.layout.addWidget(QLabel('Basic setup to ramp', self), 4, 0)
        self.layout.addWidget(self.led_ma_setup, 4, 1)
        self.layout.addWidget(self.led_rf_rmprdy, 4, 2)
        self.layout.addWidget(self.led_ti_setup, 4, 3)
        self.layout.addWidget(QLabel('Current config applied', self), 5, 0)
        self.layout.addWidget(self.led_ma_apply, 5, 1)
        self.layout.addWidget(self.led_rf_apply, 5, 2)
        self.layout.addWidget(self.led_ti_apply, 5, 3)

    def _setupCommandsLayout(self):
        self.label_commands = QLabel('<h4>Commands</h4>', self)
        self.label_commands.setStyleSheet("""
            qproperty-alignment: AlignBottom;
            min-height:1.55em; max-height:1.55em;""")

        self.bt_setup_ma = QPushButton('MA', self)
        self.bt_setup_ma.clicked.connect(self._setup_ramp_ma)
        self.bt_setup_ti = QPushButton('TI', self)
        self.bt_setup_ti.clicked.connect(self._setup_ramp_ti)
        self.bt_setup_all = QPushButton('All', self)
        self.bt_setup_all.clicked.connect(self._setup_ramp_all)

        self.bt_apply_ma = QPushButton('MA', self)
        self.bt_apply_ma.clicked.connect(self._apply_ma)
        self.bt_apply_rf = QPushButton('RF', self)
        self.bt_apply_rf.clicked.connect(self._apply_rf)
        self.bt_apply_ti = QPushButton('TI', self)
        self.bt_apply_ti.clicked.connect(self._apply_ti)
        self.bt_apply_all = QPushButton('All', self)
        self.bt_apply_all.clicked.connect(self._apply_all)

        c = self._conn_ti.Const
        self.bt_start_ramp = QPushButton('Start', self)
        self.bt_start_ramp.clicked.connect(self._start_ramp)
        self.bt_stop_ramp = QPushButton('Stop', self)
        self.bt_stop_ramp.clicked.connect(self._stop_ramp)
        self.led_ramping = SiriusLedState(
            parent=self,
            init_channel=self.prefix+c.EVG_ContinuousEvt.replace('Sel', 'Sts'))

        # Build rules to control injection commands enabling
        rule_channels = '{"channel": "' + \
            self.prefix+self._conn_rf.Const.Rmp_RmpReady+'", "trigger": true}'
        rules = (
            '[{"name": "EnblRule", "property": "Enable",' +
            '  "expression": "all([v == 1 for v in ch])",' +
            '  "channels": [' + rule_channels + ']}]')

        self.bt_start_inj = PyDMPushButton(
            parent=self, label='Start', pressValue=_TIc.DsblEnbl.Enbl,
            init_channel=self.prefix + c.EVG_InjectionEvt)
        self.bt_start_inj.rules = rules
        self.bt_stop_inj = PyDMPushButton(
            parent=self, label='Stop', pressValue=_TIc.DsblEnbl.Dsbl,
            init_channel=self.prefix + c.EVG_InjectionEvt)
        self.bt_stop_inj.rules = rules
        self.led_injecting = SiriusLedState(
            parent=self,
            init_channel=self.prefix+c.EVG_InjectionEvt.replace('Sel', 'Sts'))

        for bt in ['bt_setup_ma', 'bt_setup_ti', 'bt_setup_all',
                   'bt_apply_ma', 'bt_apply_rf', 'bt_apply_ti', 'bt_apply_all',
                   'bt_start_ramp', 'bt_stop_ramp',
                   'bt_start_inj', 'bt_stop_inj']:
            w = getattr(self, bt)
            if 'apply' in bt or 'setup' in bt:
                w.setStyleSheet("""min-width:3em; max-width:3em;
                                   min-height:1.55em; max-height: 1.55em;""")
            else:
                w.setStyleSheet("""min-height:1.55em; max-height: 1.55em;""")

        self.layout.addWidget(self.label_commands, 6, 0, 1, 6)
        self.layout.addWidget(QLabel('Basic setup to ramp: ', self), 7, 0)
        self.layout.addWidget(self.bt_setup_ma, 7, 1)
        self.layout.addWidget(self.bt_setup_ti, 7, 3)
        self.layout.addWidget(self.bt_setup_all, 7, 4)
        self.layout.addWidget(QLabel('Apply current config: ', self), 8, 0)
        self.layout.addWidget(self.bt_apply_ma, 8, 1)
        self.layout.addWidget(self.bt_apply_rf, 8, 2)
        self.layout.addWidget(self.bt_apply_ti, 8, 3)
        self.layout.addWidget(self.bt_apply_all, 8, 4)
        self.layout.addWidget(QLabel('Ramping: ', self), 9, 0)
        self.layout.addWidget(self.bt_start_ramp, 9, 1, 1, 2)
        self.layout.addWidget(self.bt_stop_ramp, 9, 3, 1, 2)
        self.layout.addWidget(self.led_ramping, 9, 5)
        self.layout.addWidget(QLabel('Injection: ', self), 10, 0)
        self.layout.addWidget(self.bt_start_inj, 10, 1, 1, 2)
        self.layout.addWidget(self.bt_stop_inj, 10, 3, 1, 2)
        self.layout.addWidget(self.led_injecting, 10, 5)

    def _setup_ramp_ma(self):
        thread = _CommandThread(
            conn=self._conn_ma,
            cmds=[self._conn_ma.cmd_pwrstate_on,
                  self._conn_ma.cmd_opmode_rmpwfm],
            warn_title='Failed to configure MA',
            warn_msgs=['Command failed to set all MA PwrState to On!',
                       'Command failed to set all MA OpMode to RmpWfm!'],
            parent=self)
        thread.start()

    def _setup_ramp_ti(self):
        thread = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_setup,
            warn_title='Failed to configure TI',
            warn_msgs='Command failed to configure TI to ramp!',
            parent=self)
        thread.start()

    def _setup_ramp_all(self):
        self._setup_ramp_ma()
        self._setup_ramp_ti()

    def _apply_ma(self):
        thread = _CommandThread(
            conn=self._conn_ma,
            cmds=self._conn_ma.cmd_wfmdata,
            warn_title='Failed to apply current RampConfig to MA',
            warn_msgs='Command failed to set all MA waveforms!',
            parent=self)
        thread.start()

    def _apply_rf(self):
        thread = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_config_ramp,
            warn_title='Failed to apply current RampConfig to RF',
            warn_msgs='Command failed to set RF parameters!',
            parent=self)
        thread.start()

    def _apply_ti(self):
        thread = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_config_ramp,
            warn_title='Failed to apply current RampConfig to TI',
            warn_msgs='Command failed to set TI parameters!',
            parent=self)
        thread.start()

    def _apply_all(self):
        self._apply_ma()
        self._apply_rf()
        self._apply_ti()

    def _start_ramp(self):
        """Start ramp.

        This action starts timing pulses and enable RF ramp.
        Power supplies and RF need to be configured to ramp.
        """
        thread_TI = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_start_ramp,
            warn_title='Failed to start ramping',
            warn_msgs='Command failed to enable TI continuous events!',
            parent=self)
        thread_RF = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_ramping_enable,
            warn_title='Failed to start ramping',
            warn_msgs='Command failed to enable RF ramp!',
            parent=self)

        thread_TI.start()
        thread_RF.start()

    def _stop_ramp(self):
        """Stop ramp.

        This action stops timing pulses and disable RF ramp.
        Power supplies and RF devices continue configured to ramp.
        """
        thread_TI = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_stop_ramp,
            warn_title='Failed to stop ramping',
            warn_msgs='Command failed to disable TI continuous events!',
            parent=self)
        thread_RF = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_ramping_disable,
            warn_title='Failed to stop ramping',
            warn_msgs='Command failed to disable RF ramp!',
            parent=self)

        thread_TI.start()
        thread_RF.start()

    @Slot(list)
    def show_warning_message(self, args):
        """Show warning message."""
        warn_msg = _MessageBox(self, args[0], args[1], 'Ok')
        warn_msg.exec_()

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Receive connectors."""
        self.ramp_config = ramp_config
        self._conn_ma.get_ramp_config(self.ramp_config)
        self._conn_ti.get_ramp_config(self.ramp_config)
        self._conn_rf.get_ramp_config(self.ramp_config)
        self.update_ma_params()
        self.update_rf_params()
        self.update_ti_params()

    def update_ma_params(self):
        """Update MA parameters leds channels2values dict."""
        if self.ramp_config:
            r = self.ramp_config
            p = self.prefix
            c2v = dict()
            for maname in self._conn_ma.manames:
                wf = r.ps_waveform_get(maname)
                c2v[p + maname + ':WfmData-RB'] = wf.currents
            self.led_ma_apply.channels2values.update(c2v)

    def update_rf_params(self):
        """Update RF parameters leds channels2values dict."""
        if self.ramp_config:
            c = self._conn_rf.Const
            r = self.ramp_config
            p = self.prefix
            c2v = dict()
            c2v[p+c.Rmp_Ts1.replace('SP', 'RB')] = r.rf_ramp_bottom_duration
            c2v[p+c.Rmp_Ts2.replace('SP', 'RB')] = r.rf_ramp_rampup_duration
            c2v[p+c.Rmp_Ts3.replace('SP', 'RB')] = r.rf_ramp_top_duration
            c2v[p+c.Rmp_Ts4.replace('SP', 'RB')] = r.rf_ramp_rampdown_duration
            c2v[p+c.Rmp_IncTs.replace('SP', 'RB')] = r.rf_ramp_rampinc_duration
            c2v[p+c.Rmp_VoltBot.replace('SP', 'RB')] = r.rf_ramp_bottom_voltage
            c2v[p+c.Rmp_VoltTop.replace('SP', 'RB')] = r.rf_ramp_top_voltage
            c2v[p+c.Rmp_PhsBot.replace('SP', 'RB')] = r.rf_ramp_bottom_phase
            c2v[p+c.Rmp_PhsTop.replace('SP', 'RB')] = r.rf_ramp_top_phase
            self.led_rf_apply.channels2values.update(c2v)

    def update_ti_params(self):
        """Update TI parameters leds channels2values dict."""
        if self.ramp_config:
            conn = self._conn_ti
            c = conn.Const
            r = self.ramp_config
            p = self.prefix
            c2v = dict()
            c2v[p+c.TrgMags_Duration.replace('SP', 'RB')] = r.ps_ramp_duration
            c2v[p+c.TrgCorrs_Duration.replace('SP', 'RB')] = r.ps_ramp_duration
            c2v[p+c.TrgMags_NrPulses.replace('SP', 'RB')] = \
                r.ps_ramp_wfm_nrpoints
            c2v[p+c.TrgCorrs_NrPulses.replace('SP', 'RB')] = \
                r.ps_ramp_wfm_nrpoints
            c2v[p+c.TrgMags_Delay.replace('SP', 'RB')] = \
                r.ti_params_ps_ramp_delay
            c2v[p+c.TrgCorrs_Delay.replace('SP', 'RB')] = \
                r.ti_params_ps_ramp_delay
            c2v[p+c.TrgLLRFRmp_Delay.replace('SP', 'RB')] = \
                r.ti_params_rf_ramp_delay
            c2v[p+c.EvtRmpBO_Delay.replace('SP', 'RB')] = 0
            [linac_dly, injbo_dly, injsi_dly] = conn.calc_evts_delay()
            c2v[p+c.EvtLinac_Delay.replace('SP', 'RB')] = linac_dly
            c2v[p+c.EvtInjBO_Delay.replace('SP', 'RB')] = injbo_dly
            c2v[p+c.EvtInjSI_Delay.replace('SP', 'RB')] = injsi_dly
            self.led_ti_apply.channels2values.update(c2v)


class _CommandThread(QThread):
    """Thread to perform commands."""

    sentWarning = Signal(list)

    def __init__(self, conn, cmds, warn_title='', warn_msgs=list(),
                 timeout=COMMANDS_TIMEOUT, parent=None):
        """Initialize."""
        super().__init__(parent)
        self._conn = conn
        self._subsystem = self._get_subsystem()
        self._cmds = cmds
        self._warn_title = warn_title
        self._warn_msgs = warn_msgs
        self._timeout = timeout
        self.sentWarning.connect(parent.show_warning_message)

    def _get_subsystem(self):
        conn_name = self._conn.__class__.__name__
        if conn_name == 'ConnMagnets':
            return 'MA'
        elif conn_name == 'ConnTiming':
            return 'TI'
        elif conn_name == 'ConnRF':
            return 'RF'
        elif conn_name == 'ConnSOFB':
            return 'SOFB'

    def _verify_connector(self):
        if not self._conn:
            return False
        if not self._conn.connected:
            self.sentWarning.emit(
                ['Not Connected',
                 'There are not connected PVs in {}!'.format(self._subsystem)])
            return False
        return True

    def run(self):
        """Run."""
        if not self._verify_connector():
            return
        if not isinstance(self._cmds, list):
            self._cmds = [self._cmds, ]
        if not isinstance(self._warn_msgs, list):
            self._warn_msgs = [self._warn_msgs, ]
        for cmd, msg in zip(self._cmds, self._warn_msgs):
            cmd_success = cmd(self._timeout)
            if not cmd_success:
                self.sentWarning.emit([self._warn_title, msg])
