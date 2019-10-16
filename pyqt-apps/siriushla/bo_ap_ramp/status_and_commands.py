"""Booster Ramp Control HLA: General Status Module."""

from functools import partial as _part
from threading import Thread as _Thread
import numpy as _np
import time as _time
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, \
    QMessageBox, QVBoxLayout, QComboBox
from qtpy.QtCore import Qt, Slot, Signal, QThread
import qtawesome as qta

from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming
from siriuspy.csdevice.pwrsupply import Const as _PSc
from siriuspy.csdevice.timesys import Const as _TIc

from siriushla.widgets import PyDMLedMultiChannel, PyDMLedMultiConnection, \
                              SiriusDialog

EVT_LIST = ['Linac', 'InjBO', 'InjSI', 'Study',
            'DigLI', 'DigTB', 'DigBO', 'DigTS', 'DigSI']


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    inj_eje_times = Signal(float, float)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._setupUi()
        thread = _Thread(target=self._create_connectors, daemon=True)
        thread.start()

    def _setupUi(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addLayout(self._setupStatusLayout())
        lay.addStretch()
        lay.addLayout(self._setupChooseTIEventLayout())
        lay.addStretch()
        lay.addLayout(self._setupCommandsLayout())
        self.setLayout(lay)

        self.setStyleSheet("""
            QLabel{
                qproperty-alignment: AlignCenter;
                min-height:1.55em; max-height:1.55em;
                max-width:10em;}""")

    def _setupStatusLayout(self):
        self.led_conn = PyDMLedMultiConnection(self)
        self.led_intlk = PyDMLedMultiChannel(self)
        self.led_setup = PyDMLedMultiChannel(self)
        self.led_apply = PyDMLedMultiChannel(self)
        self.pb_opendetails = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.pb_opendetails.clicked.connect(self._open_status_details)
        self.pb_opendetails.setStyleSheet(
            'icon-size: 16px 16px; max-height:1.29em; max-width:2em;')

        lay = QGridLayout()
        lay.setVerticalSpacing(10)
        lay.addWidget(QLabel('<h4>Status</h4>', self), 0, 0)
        lay.addWidget(self.pb_opendetails, 0, 1, alignment=Qt.AlignRight)
        lay.addWidget(QLabel('Connection', self), 1, 0)
        lay.addWidget(self.led_conn, 1, 1)
        lay.addWidget(QLabel('Interlock', self), 2, 0)
        lay.addWidget(self.led_intlk, 2, 1)
        lay.addWidget(QLabel('Basic Setup', self), 3, 0)
        lay.addWidget(self.led_setup, 3, 1)
        lay.addWidget(QLabel('Config Applied?', self), 4, 0)
        lay.addWidget(self.led_apply, 4, 1)
        return lay

    def _setupCommandsLayout(self):
        self.bt_prepare_ma = QPushButton('Prepare magnets', self)
        self.bt_prepare_ma.clicked.connect(self._prepare_ma)
        self.bt_prepare_ma.setStyleSheet('min-height:1.5em;')
        self.bt_prepare_rf = QPushButton('Prepare RF', self)
        self.bt_prepare_rf.clicked.connect(self._prepare_rf)
        self.bt_prepare_rf.setStyleSheet('min-height:1.5em;')
        self.bt_prepare_ti = QPushButton('Prepare timing', self)
        self.bt_prepare_ti.clicked.connect(self._prepare_ti)
        self.bt_prepare_ti.setStyleSheet('min-height:1.5em;')

        icon_all = qta.icon('fa5s.angle-double-right')
        self.bt_apply_all = QPushButton(icon_all, '', self)
        self.bt_apply_all.setToolTip('Apply All Changes to Machine')
        self.bt_apply_all.setObjectName('All')
        self.bt_apply_all.clicked.connect(self.apply_changes)
        self.bt_apply_all.setStyleSheet(
            'icon-size: 35px 35px;')

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)
        lay.addStretch()
        lay.addWidget(self.bt_prepare_ma)
        lay.addWidget(self.bt_prepare_rf)
        lay.addWidget(self.bt_prepare_ti)
        lay.addStretch()
        lay.addWidget(self.bt_apply_all)
        return lay

    def _setupChooseTIEventLayout(self):
        lay = QGridLayout()
        lay.setVerticalSpacing(3)
        lay.addWidget(QLabel('Control events:'), 0, 0, 1, 2)
        for i, ev in enumerate(EVT_LIST):
            lb = QLabel(ev, self)
            cb = QComboBox(self)
            cb.addItems(['None', 'Inj', 'Eje'])
            if ev in ['Linac', 'InjBO']:
                cb.setCurrentText('Inj')
                cb.setEnabled(False)
            elif ev == 'InjSI':
                cb.setCurrentText('Eje')
                cb.setEnabled(False)
            else:
                cb.setCurrentText('None')
                cb.setEnabled(True)
            cb.setObjectName(ev)
            lay.addWidget(lb, i+1, 0)
            lay.addWidget(cb, i+1, 1)
        return lay

    def _create_connectors(self):
        # Create connectors
        self._conn_ma = _ConnMagnets(prefix=self.prefix)
        self._conn_ti = _ConnTiming(prefix=self.prefix)
        self._conn_rf = _ConnRF(prefix=self.prefix)

        # Build leds channels
        pfx = self.prefix
        c2v_conn = list()
        c2v_intlk = dict()
        c2v_setup = dict()
        c2v_apply = dict()

        for conn in [self._conn_ma, self._conn_rf, self._conn_ti]:
            for p in conn.properties:
                if 'Magnets' in conn.__class__.__name__:
                    if 'PwrState' in conn[p].name:
                        c2v_conn.append(pfx + conn[p].pvname_rb)
                else:
                    c2v_conn.append(pfx + conn[p].pvname_rb)

        conn = self._conn_ma
        for p in conn.properties:
            if 'IntlkSoft' in p or 'IntlkHard' in p:
                c2v_intlk[pfx + conn[p].pvname_rb] = 0
            elif 'OpMode' in p:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.States.RmpWfm
            elif 'PwrState' in p:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.PwrStateSts.On
            elif 'Wfm' in p:
                c2v_apply[pfx + conn[p].pvname_rb] = {'value': _np.array([]),
                                                      'comp': 'cl',
                                                      'abs_tol': 1e-5}

        conn = self._conn_rf
        c2v_intlk[pfx + conn.Const.Rmp_Intlk] = 0
        c2v_setup[pfx + conn.Const.Rmp_RmpReady] = 1
        c2v_setup[pfx + conn.Const.Rmp_IncTs] = 0.0
        c2v_apply[pfx + conn.Const.Rmp_Ts1.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts2.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts3.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts4.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_VoltBot.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_VoltTop.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_PhsBot.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_PhsTop.replace('SP', 'RB')] = None

        conn = self._conn_ti
        c2v_intlk[pfx + conn.Const.Intlk] = 0
        for prpty, value in conn.ramp_basicsetup.items():
            c2v_setup[pfx + prpty] = value
        for prpty, value in conn.ramp_configsetup.items():
            c2v_apply[pfx + prpty] = {'value': value,
                                      'comp': 'cl', 'abs_tol': 0.008}

        self.led_conn.set_channels(c2v_conn)
        self.led_intlk.set_channels2values(c2v_intlk)
        self.led_setup.set_channels2values(c2v_setup)
        self.led_apply.set_channels2values(c2v_apply)

    def _prepare_ma(self):
        # turn off triggers
        thread = _CommandThread(
            conn=self._conn_ti, cmds=_part(
                self._conn_ti.cmd_set_magnet_trigger_state,
                _TIc.DsblEnbl.Dsbl),
            warn_msgs='Failed to turn magnets trigger off!', parent=self)
        thread.start()
        _time.sleep(1)
        # set magnets opmode
        thread = _CommandThread(
            conn=self._conn_ma, cmds=self._conn_ma.cmd_opmode_rmpwfm,
            warn_msgs='Failed to set MA OpMode to RmpWfm!', parent=self)
        thread.start()
        _time.sleep(1)
        # turn on triggers
        thread = _CommandThread(
            conn=self._conn_ti, cmds=_part(
                self._conn_ti.cmd_set_magnet_trigger_state,
                _TIc.DsblEnbl.Enbl),
            warn_msgs='Failed to turn magnets trigger on!', parent=self)
        thread.start()

    def _prepare_rf(self):
        thread_RF = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_ramping_enable,
            warn_msgs='Failed to enable RF ramp!',
            parent=self)
        thread_RF.start()

    def _prepare_ti(self):
        thread = _CommandThread(
            conn=self._conn_ti,
            cmds=self._conn_ti.cmd_setup,
            warn_msgs='Failed to setup TI to ramp!',
            parent=self)
        thread.start()

    def _apply_ma(self, manames=list()):
        thread = _CommandThread(
            conn=self._conn_ma,
            cmds=_part(self._conn_ma.cmd_wfm, manames),
            warn_msgs='Failed to set MA waveforms!',
            parent=self)
        thread.start()

    def _apply_rf(self):
        thread = _CommandThread(
            conn=self._conn_rf,
            cmds=self._conn_rf.cmd_config_ramp,
            warn_msgs='Failed to set RF parameters!',
            parent=self)
        thread.start()

    def _apply_ti(self):
        events_inj, events_eje = self._get_inj_eje_events()
        thread = _CommandThread(
            conn=self._conn_ti,
            cmds=_part(self._conn_ti.cmd_config_ramp,
                       events_inj, events_eje),
            warn_msgs='Failed to set TI parameters!',
            parent=self)
        thread.start()
        # update values of inj and eje times in fact implemented
        _time.sleep(3)
        inj_time = self._conn_ti.get_injection_time()/1000  # [ms]
        eje_time = self._conn_ti.get_ejection_time()/1000  # [ms]
        self.inj_eje_times.emit(inj_time, eje_time)

    def _open_status_details(self):
        self.status_details = StatusDetails(
            self, prefix=self.prefix, ramp_config=self.ramp_config,
            connMA=self._conn_ma, connTI=self._conn_ti, connRF=self._conn_rf)
        self.status_details.open()

    def apply_changes(self):
        if self.ramp_config is None:
            return

        sender_name = self.sender().objectName()

        manames = list()
        if not self.ramp_config.ps_normalized_configs:
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Warning)
            mb.setWindowTitle('Message')
            if 'Dipole' in sender_name or 'All' in sender_name:
                manames = ['BO-Fam:MA-B', ]
                msg = 'Only Dipole will be applied because there is no '\
                      'normalized configuration defined!'
                mb.setText(msg)
                mb.exec_()
            elif 'Multipoles' in sender_name:
                msg = 'Nothing applied! No normalized configuration defined!'
                mb.setText(msg)
                mb.exec_()
                return

        if 'Dipole' in sender_name:
            self._apply_ma(manames)
            self._apply_ti()
        elif 'Multipoles' in sender_name:
            self._apply_ma(manames)
        elif 'RF' in sender_name:
            self._apply_rf()
            self._apply_ti()
        elif 'All' in sender_name:
            self._apply_ma(manames)
            self._apply_rf()
            self._apply_ti()

    @Slot(str)
    def show_warning_message(self, msg):
        """Show warning message."""
        mb = QMessageBox()
        mb.setMinimumSize(300, 150)
        mb.setWindowTitle('Message')
        mb.setIcon(QMessageBox.Warning)
        mb.setText(msg)
        mb.exec()

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
        if self.ramp_config is None:
            return
        if not self.ramp_config.ps_normalized_configs:
            return
        c2v = dict()
        for maname in self._conn_ma.manames:
            wf = self.ramp_config.ps_waveform_get(maname)
            c2v[self.prefix + maname + ':Wfm-RB'] = {
                'value': wf.currents, 'comp': 'cl', 'abs_tol': 1e-5}
        self.led_apply.channels2values.update(c2v)

    def update_rf_params(self):
        """Update RF parameters leds channels2values dict."""
        if self.ramp_config is None:
            return
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
        self.led_apply.channels2values.update(c2v)

    def update_ti_params(self):
        """Update TI parameters leds channels2values dict."""
        if self.ramp_config is None:
            return
        conn = self._conn_ti
        c = conn.Const
        r = self.ramp_config
        p = self.prefix
        c2v = dict()
        c2v[p+c.TrgMags_Duration.replace('SP', 'RB')] = r.ps_ramp_duration
        c2v[p+c.TrgCorrs_Duration.replace('SP', 'RB')] = r.ps_ramp_duration

        c2v[p+c.TrgMags_NrPulses.replace('SP', 'RB')] = \
            r.ps_ramp_wfm_nrpoints_fams
        c2v[p+c.TrgCorrs_NrPulses.replace('SP', 'RB')] = \
            r.ps_ramp_wfm_nrpoints_corrs

        c2v[p+c.TrgMags_Delay.replace('SP', 'RB')] = r.ti_params_ps_ramp_delay
        c2v[p+c.TrgCorrs_Delay.replace('SP', 'RB')] = r.ti_params_ps_ramp_delay
        c2v[p+c.TrgLLRFRmp_Delay.replace('SP', 'RB')] = \
            r.ti_params_rf_ramp_delay
        c2v[p+c.EvtRmpBO_Delay.replace('SP', 'RB')] = 0.0

        events_inj, events_eje = self._get_inj_eje_events()
        delays = conn.calc_evts_delay(events_inj, events_eje)
        if not delays:
            self.show_warning_message('There are TI not connected PVs!')
            delays = {ev: None for ev in EVT_LIST}
        else:
            conn.update_ramp_configsetup(events_inj, events_eje, delays)

        for ev in events_inj:
            attr = getattr(c, 'Evt'+ev+'_Delay')
            attr = attr.replace('SP', 'RB')
            c2v[p+attr] = delays[ev]
        for ev in events_eje:
            attr = getattr(c, 'Evt'+ev+'_Delay')
            attr = attr.replace('SP', 'RB')
            c2v[p+attr] = delays[ev]
        for ev in EVT_LIST:
            if ev in events_inj or ev in events_eje:
                continue
            attr = getattr(c, 'Evt'+ev+'_Delay')
            c2v[p+attr] = None
        self.led_apply.channels2values.update(c2v)

    def _get_inj_eje_events(self):
        events_inj = list()
        events_eje = list()
        for ev in EVT_LIST:
            cb = self.findChild(QComboBox, ev)
            if cb.currentText() == 'Inj':
                events_inj.append(ev)
            elif cb.currentText() == 'Eje':
                events_eje.append(ev)
        return events_inj, events_eje


class _CommandThread(QThread):
    """Thread to perform commands."""

    sentWarning = Signal(str)

    def __init__(self, conn, cmds, warn_msgs=list(), parent=None):
        """Initialize."""
        super().__init__(parent)
        self._conn = conn
        self._subsystem = self._get_subsystem()
        self._cmds = cmds
        self._warn_msgs = warn_msgs
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
                'There are not connected PVs in {}!'.format(self._subsystem))
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
            cmd_success = cmd()
            if not cmd_success:
                self.sentWarning.emit(msg)


class StatusDetails(SiriusDialog):
    """Status details."""

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 connMA=None, connTI=None, connRF=None):
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._conn_ma = connMA or _ConnMagnets(prefix=self.prefix)
        self._conn_ti = connTI or _ConnTiming(prefix=self.prefix)
        self._conn_rf = connRF or _ConnRF(prefix=self.prefix)
        self._setupUi()
        t = _Thread(target=self._print, daemon=True)
        t.start()

    def _setupUi(self):
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
            if 'IntlkSoft' in p or 'IntlkHard' in p:
                c2v_intlk[pfx + conn[p].pvname_rb] = 0
            elif 'OpMode' in p:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.States.RmpWfm
            elif 'PwrState' in p:
                c2v_setup[pfx + conn[p].pvname_rb] = _PSc.PwrStateSts.On
            elif 'Wfm' in p:
                if self.ramp_config is None or \
                        not self.ramp_config.ps_normalized_configs:
                    c2v_apply[pfx + conn[p].pvname_rb] = {
                        'value': _np.array([]), 'comp': 'cl', 'abs_tol': 1e-5}
                elif self.ramp_config.ps_normalized_configs:
                    wf = self.ramp_config.ps_waveform_get(p.device_name)
                    c2v_apply[pfx + conn[p].pvname_rb] = {
                        'value': wf.currents, 'comp': 'cl', 'abs_tol': 1e-5}

        self.led_ma_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_ma_setup = PyDMLedMultiChannel(self, c2v_setup)
        self.led_ma_apply = PyDMLedMultiChannel(self, c2v_apply)

        # RF Leds
        conn = self._conn_rf
        c2v_intlk = {pfx + conn.Const.Rmp_Intlk: 0}
        c2v_setup = {pfx + conn.Const.Rmp_RmpReady: 1,
                     pfx + conn.Const.Rmp_IncTs: 0}
        c2v_apply = dict()
        c2v_apply[pfx + conn.Const.Rmp_Ts1.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts2.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts3.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_Ts4.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_VoltBot.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_VoltTop.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_PhsBot.replace('SP', 'RB')] = 0
        c2v_apply[pfx + conn.Const.Rmp_PhsTop.replace('SP', 'RB')] = 0

        self.led_rf_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_rf_rmprdy = PyDMLedMultiChannel(self, c2v_setup)
        self.led_rf_apply = PyDMLedMultiChannel(self, c2v_apply)

        # TI Leds
        conn = self._conn_ti
        c2v_intlk = {pfx + conn.Const.Intlk: 0}
        c2v_setup = dict()
        for prpty, value in conn.ramp_basicsetup.items():
            c2v_setup[pfx + prpty] = value
        c2v_apply = dict()
        for prpty, value in conn.ramp_configsetup.items():
            c2v_apply[pfx + prpty] = {'value': value,
                                      'comp': 'cl', 'abs_tol': 0.008}

        self.led_ti_intlk = PyDMLedMultiChannel(self, c2v_intlk)
        self.led_ti_setup = PyDMLedMultiChannel(self, c2v_setup)
        self.led_ti_apply = PyDMLedMultiChannel(self, c2v_apply)

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
        self.setLayout(glay)

    def _print(self):
        led = self.led_ma_apply
        _time.sleep(4)
        for k, v in led.channels2values.items():
            print(k, v)
        print('')
        for k, v in led.channels2status.items():
            print(k, v)
        print('\n\n')
