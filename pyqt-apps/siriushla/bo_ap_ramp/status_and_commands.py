"""Booster Ramp Control HLA: General Status Module."""

from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, \
    QMessageBox, QHBoxLayout, QVBoxLayout
from qtpy.QtCore import Slot, Signal, QThread
from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming
from siriuspy.csdevice.pwrsupply import Const as _PSc
from siriushla.widgets import PyDMLedMultiChannel, PyDMLedMultiConnection, \
                              SiriusLedState, PyDMStateButton

COMMANDS_TIMEOUT = 1


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Controls', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._conn_ma = _ConnMagnets(prefix=self.prefix)
        self._conn_ti = _ConnTiming(prefix=self.prefix)
        self._conn_rf = _ConnRF(prefix=self.prefix)
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout()
        lay.setSpacing(10)
        lay.addLayout(self._setupStatusLayout())
        lay.addLayout(self._setupCommandsLayout())
        self.setLayout(lay)

        self.setStyleSheet("""
            QLabel{
                qproperty-alignment: AlignCenter;
                min-height:1.55em; max-height:1.55em;
                max-width:10em;}
            PyDMLedMultiChannel, PyDMLedMultiConnection{
                min-width:3em; max-width:3em;}
            #RampGb, #InjectGb{
                max-height:4em;
                min-width:7em; max-width:7em;}""")

    def _setupStatusLayout(self):
        pfx = self.prefix

        # Connection Leds
        for led_name in ['led_ma_conn', 'led_rf_conn', 'led_ti_conn']:
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

        glay = QGridLayout()
        glay.addWidget(QLabel('<h4>Status</h4>'), 1, 0, 1, 4)
        glay.addWidget(self.label_ma, 1, 1)
        glay.addWidget(self.label_rf, 1, 2)
        glay.addWidget(self.label_ti, 1, 3)
        glay.addWidget(QLabel('Connection', self), 2, 0)
        glay.addWidget(self.led_ma_conn, 2, 1)
        glay.addWidget(self.led_rf_conn, 2, 2)
        glay.addWidget(self.led_ti_conn, 2, 3)
        glay.addWidget(QLabel('Interlocks', self), 3, 0)
        glay.addWidget(self.led_ma_intlk, 3, 1)
        glay.addWidget(self.led_rf_intlk, 3, 2)
        glay.addWidget(self.led_ti_intlk, 3, 3)
        glay.addWidget(QLabel('Basic setup to ramp', self), 4, 0)
        glay.addWidget(self.led_ma_setup, 4, 1)
        glay.addWidget(self.led_rf_rmprdy, 4, 2)
        glay.addWidget(self.led_ti_setup, 4, 3)
        glay.addWidget(QLabel('Current config applied', self), 5, 0)
        glay.addWidget(self.led_ma_apply, 5, 1)
        glay.addWidget(self.led_rf_apply, 5, 2)
        glay.addWidget(self.led_ti_apply, 5, 3)
        return glay

    def _setupCommandsLayout(self):
        self.bt_setup = QPushButton('Setup subsystems', self)
        self.bt_setup.clicked.connect(self._setup_ramp)

        c = self._conn_ti.Const

        gbox_ramp = QGroupBox('Ramp', self)
        gbox_ramp.setObjectName('RampGb')
        hlay = QHBoxLayout(gbox_ramp)
        self.bt_ramp = PyDMStateButton(
            parent=self, init_channel=self.prefix+c.EVG_ContinuousEvt)
        self.led_ramp = SiriusLedState(
            parent=self, init_channel=self.prefix+c.EVG_ContinuousEvt.replace(
                                      'Sel', 'Sts'))
        hlay.addWidget(self.bt_ramp)
        hlay.addWidget(self.led_ramp)

        gbox_inject = QGroupBox('Inject', self)
        gbox_inject.setObjectName('InjectGb')
        hlay = QHBoxLayout(gbox_inject)
        self.bt_inject = PyDMStateButton(
            parent=self, init_channel=self.prefix+c.EVG_InjectionEvt)
        self.led_inject = SiriusLedState(
            parent=self, init_channel=self.prefix+c.EVG_InjectionEvt.replace(
                                      'Sel', 'Sts'))
        hlay.addWidget(self.bt_inject)
        hlay.addWidget(self.led_inject)

        glay = QGridLayout()
        label = QLabel('<h4>Commands</h4>', self)
        label.setStyleSheet('max-width:20em;')
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.bt_setup, 1, 0, 1, 2)
        glay.addWidget(gbox_ramp, 2, 0)
        glay.addWidget(gbox_inject, 2, 1)
        return glay

    def _setup_ramp(self):
        # MA
        thread = _CommandThread(
            conn=self._conn_ma,
            cmds=[self._conn_ma.cmd_opmode_slowref,
                  self._conn_ma.cmd_pwrstate_on,
                  self._conn_ma.cmd_opmode_rmpwfm],
            warn_title='Failed to setup MA',
            warn_msgs=[
                'Command failed to set all MA OpMode to SlowRef!',
                'Command failed to set all MA PwrState to On!',
                'Command failed to set all MA OpMode to RmpWfm!'],
            parent=self)
        thread.start()

        # RF
        thread_RF = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_ramping_enable,
            warn_title='Failed to setup RF',
            warn_msgs='Command failed to enable RF ramp!',
            parent=self)
        thread_RF.start()

        # TI
        thread = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_setup,
            warn_title='Failed to setup TI',
            warn_msgs='Command failed to setup TI to ramp!',
            parent=self)
        thread.start()

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

    def apply_changes(self):
        if not self.ramp_config:
            return

        sender_name = self.sender().objectName()
        if 'Dipole' in sender_name:
            self._apply_ma()
            self._apply_ti()
        elif 'Multipoles' in sender_name:
            self._apply_ma()
        elif 'RF' in sender_name:
            self._apply_rf()

    @Slot(list)
    def show_warning_message(self, args):
        """Show warning message."""
        QMessageBox.warning(self, args[0], args[1], QMessageBox.Ok)

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
            c2v = dict()
            for maname in self._conn_ma.manames:
                wf = self.ramp_config.ps_waveform_get(maname)
                c2v[self.prefix + maname + ':WfmData-RB'] = wf.currents
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
            params = conn.calc_evts_delay()
            if not params:
                QMessageBox.critical(self, 'Timing not connected',
                                     'There are TI not connected PVs!',
                                     QMessageBox.Ok)
                params = [None]*3
            c2v[p+c.EvtLinac_Delay.replace('SP', 'RB')] = params[0]
            c2v[p+c.EvtInjBO_Delay.replace('SP', 'RB')] = params[1]
            c2v[p+c.EvtInjSI_Delay.replace('SP', 'RB')] = params[2]
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
