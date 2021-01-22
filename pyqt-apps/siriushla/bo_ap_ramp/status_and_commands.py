"""Booster Ramp Control HLA: General Status Module."""

from functools import partial as _part
import time as _time
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QGridLayout, \
    QMessageBox, QVBoxLayout, QComboBox
from qtpy.QtCore import Qt, Slot, Signal, QThread
import qtawesome as qta

from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnPS as _ConnPS, ConnRF as _ConnRF,\
    ConnTI as _ConnTI
from siriuspy.pwrsupply.csdev import Const as _PSc
from siriuspy.timesys.csdev import Const as _TIc

from siriushla.widgets import PyDMLedMultiChannel, PyDMLedMultiConnection
from siriushla.widgets.dialog import ProgressDialog

EVT_LIST = ['Linac', 'InjBO', 'InjSI', 'Study',
            'DigLI', 'DigTB', 'DigBO', 'DigTS', 'DigSI']


class StatusAndCommands(QGroupBox):
    """Widget to show general Booster timing and power supplies status."""

    inj_eje_times = Signal(float, float)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._setupUi()
        self.conn_ps = None
        self.conn_rf = None
        self.conn_ti = None
        th = _createConnectorsThread(self, prefix)
        th.start()

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
                min-height:1.55em; max-height:1.55em;}""")

    def _setupStatusLayout(self):
        self.led_ps_conn = PyDMLedMultiConnection(self)
        self.led_ps_intlk = PyDMLedMultiChannel(self)
        self.led_ps_setup = PyDMLedMultiChannel(self)
        self.led_ps_apply = PyDMLedMultiChannel(self)
        self.led_rf_conn = PyDMLedMultiConnection(self)
        self.led_rf_intlk = PyDMLedMultiChannel(self)
        self.led_rf_setup = PyDMLedMultiChannel(self)
        self.led_rf_apply = PyDMLedMultiChannel(self)
        self.led_ti_conn = PyDMLedMultiConnection(self)
        self.led_ti_intlk = PyDMLedMultiChannel(self)
        self.led_ti_setup = PyDMLedMultiChannel(self)
        self.led_ti_apply = PyDMLedMultiChannel(self)

        lay = QGridLayout()
        lay.addWidget(QLabel('<h4>Status</h4>'), 1, 0)
        lay.addWidget(QLabel('<h4>PS</h4>'), 1, 1)
        lay.addWidget(QLabel('<h4>RF</h4>'), 1, 2)
        lay.addWidget(QLabel('<h4>TI</h4>'), 1, 3)
        lay.addWidget(QLabel('Connection', self), 2, 0)
        lay.addWidget(self.led_ps_conn, 2, 1)
        lay.addWidget(self.led_rf_conn, 2, 2)
        lay.addWidget(self.led_ti_conn, 2, 3)
        lay.addWidget(QLabel('Interlocks', self), 3, 0)
        lay.addWidget(self.led_ps_intlk, 3, 1)
        lay.addWidget(self.led_rf_intlk, 3, 2)
        lay.addWidget(self.led_ti_intlk, 3, 3)
        lay.addWidget(QLabel('Basic Setup', self), 4, 0)
        lay.addWidget(self.led_ps_setup, 4, 1)
        lay.addWidget(self.led_rf_setup, 4, 2)
        lay.addWidget(self.led_ti_setup, 4, 3)
        lay.addWidget(QLabel('Config Applied', self), 5, 0)
        lay.addWidget(self.led_ps_apply, 5, 1)
        lay.addWidget(self.led_rf_apply, 5, 2)
        lay.addWidget(self.led_ti_apply, 5, 3)
        return lay

    def _setupCommandsLayout(self):
        self.bt_prepare_ps = QPushButton('Prepare magnets', self)
        self.bt_prepare_ps.clicked.connect(self._prepare_ps)
        self.bt_prepare_ps.setStyleSheet('min-height:1.5em;')
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
        lay.addWidget(self.bt_prepare_ps)
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
            cb.currentTextChanged.connect(self.update_ti_params)
            lay.addWidget(lb, i+1, 0)
            lay.addWidget(cb, i+1, 1)
        return lay

    def _prepare_ps(self):
        tasks = [None]*3
        tasks[0] = _CommandThread(
            parent=self, conn=self.conn_ti,
            cmds=_part(self.conn_ti.cmd_set_magnet_trigger_state,
                       _TIc.DsblEnbl.Dsbl),
            warn_msgs='Failed to turn magnets trigger off!')
        tasks[1] = _CommandThread(
            parent=self, conn=self.conn_ps, use_log=True,
            cmds=self.conn_ps.cmd_opmode_rmpwfm,
            warn_msgs='Failed to set PS OpMode to RmpWfm!')
        tasks[2] = _CommandThread(
            parent=self, conn=self.conn_ti,
            cmds=_part(self.conn_ti.cmd_set_magnet_trigger_state,
                       _TIc.DsblEnbl.Enbl),
            warn_msgs='Failed to turn magnets trigger on!')

        labels = ['Turning magnets trigger off...',
                  'Setting power supplies OpMode to RmpWfm...',
                  'Turning magnets trigger on...']
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _prepare_ti(self):
        task = _CommandThread(
            parent=self, conn=self.conn_ti,
            cmds=[self.conn_ti.cmd_setup, self.conn_ti.cmd_update_evts],
            warn_msgs=['Failed to setup TI to ramp!',
                       'Failed to update events!'])
        dlg = ProgressDialog('Preparing TI to ramp...', task, self)
        dlg.exec_()

    def _apply_ps(self, psnames=list(), dialog_parent=None):
        if dialog_parent is None:
            dialog_parent = self
        task = _CommandThread(
            parent=self, conn=self.conn_ps, use_log=True, size=len(psnames),
            cmds=_part(self.conn_ps.cmd_wfm, psnames),
            warn_msgs='Failed to set waveform!')
        dlg = ProgressDialog(
            'Setting magnets waveforms...', task, dialog_parent)
        dlg.exec_()

    def _apply_rf(self, dialog_parent=None):
        if dialog_parent is None:
            dialog_parent = self
        task = _CommandThread(
            parent=self, conn=self.conn_rf, use_log=True,
            cmds=self.conn_rf.cmd_config_ramp,
            warn_msgs='Failed to set RF parameters!')
        dlg = ProgressDialog('Setting RF parameters...', task, dialog_parent)
        dlg.exec_()

    def _apply_ti(self, dialog_parent=None):
        if dialog_parent is None:
            dialog_parent = self
        events_inj, events_eje = self._get_inj_eje_events()
        task = _CommandThread(
            conn=self.conn_ti, parent=self,
            cmds=[_part(self.conn_ti.cmd_config_ramp,
                        events_inj, events_eje),
                  self.conn_ti.cmd_update_evts],
            warn_msgs=['Failed to set TI parameters!',
                       'Failed to update events!'])
        dlg = ProgressDialog('Setting TI parameters...', task, dialog_parent)
        dlg.exec_()
        # update values of inj and eje times in fact implemented
        _time.sleep(3)
        inj_time = self.conn_ti.get_injection_time()/1000  # [ms]
        eje_time = self.conn_ti.get_ejection_time()/1000  # [ms]
        self.inj_eje_times.emit(inj_time, eje_time)

    def apply_changes(self, dialog_parent=None):
        if self.ramp_config is None:
            return
        if dialog_parent is None:
            dialog_parent = self

        sender_name = self.sender().objectName()

        psnames = list()
        if not self.ramp_config.ps_normalized_configs:
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Warning)
            mb.setWindowTitle('Message')
            if 'Dipole' in sender_name or 'All' in sender_name:
                psnames = ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']
                msg = 'Only Dipole will be applied because there is no '\
                      'normalized configuration defined!'
                mb.setText(msg)
                mb.exec_()
            elif 'Multipoles' in sender_name:
                msg = 'Nothing applied! No normalized configuration defined!'
                mb.setText(msg)
                mb.exec_()
                return
        else:
            psnames = self.conn_ps.psnames

        if 'Dipole' in sender_name:
            self._apply_ps(psnames, dialog_parent)
            self._apply_ti(dialog_parent)
        elif 'Multipoles' in sender_name:
            self._apply_ps(psnames, dialog_parent)
        elif 'RF' in sender_name:
            self._apply_rf(dialog_parent)
            self._apply_ti(dialog_parent)
        elif 'All' in sender_name:
            self._apply_ps(psnames, dialog_parent)
            self._apply_rf(dialog_parent)
            self._apply_ti(dialog_parent)

    @Slot(str, list)
    def show_warning_message(self, msg, problems):
        """Show warning message."""
        text = msg + '\n\nVerify PVs:\n'
        for problem in problems:
            text += problem + '\n'
        mb = QMessageBox()
        mb.setMinimumSize(300, 150)
        mb.setWindowTitle('Message')
        mb.setIcon(QMessageBox.Warning)
        mb.setText(text)
        mb.exec()

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Receive connectors."""
        self.ramp_config = ramp_config
        self.conn_ps.get_ramp_config(self.ramp_config)
        self.conn_ti.get_ramp_config(self.ramp_config)
        self.conn_rf.get_ramp_config(self.ramp_config)
        self.update_ps_params()
        self.update_rf_params()
        self.update_ti_params()

    def update_ps_params(self):
        """Update PS parameters leds channels2values dict."""
        if self.ramp_config is None:
            return
        if not self.ramp_config.ps_normalized_configs:
            psnames = ramp.BoosterRamp.PSNAME_DIPOLES
        else:
            psnames = self.conn_ps.psnames
        c2v = dict()
        for psname in psnames:
            wf = self.ramp_config.ps_waveform_get(psname)
            c2v[self.prefix + psname + ':WfmRef-Mon'] = {
                'value': wf.currents, 'comp': 'cl', 'abs_tol': 1e-5}
        self.led_ps_apply.set_channels2values(c2v)

    def update_rf_params(self):
        """Update RF parameters leds channels2values dict."""
        if self.ramp_config is None:
            return
        d2c = self.conn_rf.get_propty_2_config_ramp_dict()
        c2v = dict()
        for pv, val in d2c.items():
            c2v[self.prefix+pv.replace('SP', 'RB')] = {
                'value': val, 'comp': 'cl', 'rel_tol': 0.001}
        self.led_rf_apply.set_channels2values(c2v)

    def update_ti_params(self):
        """Update TI parameters leds channels2values dict."""
        if self.ramp_config is None:
            return
        conn = self.conn_ti
        c = conn.Const
        r = self.ramp_config
        p = self.prefix
        c2v = dict()

        c2v[p+c.TrgMags_Delay.replace('SP', 'RB')] =  \
            {'value': r.ti_params_ps_ramp_delay, 'comp': 'cl',
             'abs_tol': 0.008}
        c2v[p+c.TrgCorrs_Delay.replace('SP', 'RB')] = \
            {'value': r.ti_params_ps_ramp_delay, 'comp': 'cl',
             'abs_tol': 0.008}
        c2v[p+c.TrgLLRFRmp_Delay.replace('SP', 'RB')] = \
            {'value': r.ti_params_rf_ramp_delay, 'comp': 'cl',
             'abs_tol': 0.008}

        c2v[p+c.EvtRmpBO_Delay.replace('SP', 'RB')] = \
            {'value': 0.0, 'comp': 'cl', 'abs_tol': 0.008}

        events_inj, events_eje = self._get_inj_eje_events()
        delays = conn.calc_evts_delay(events_inj, events_eje)
        if not delays:
            self.show_warning_message('There are TI not connected PVs!',
                                      conn.disconnected_properties)
            delays = {ev: None for ev in EVT_LIST}
        else:
            conn.update_ramp_configsetup(events_inj, events_eje, delays)

        for ev in EVT_LIST:
            attr = getattr(c, 'Evt'+ev+'_Delay')
            attr = attr.replace('SP', 'RB')
            c2v[p+attr] = None \
                if (ev not in delays.keys() or delays[ev] is None) \
                else {'value': delays[ev], 'comp': 'cl', 'abs_tol': 0.008}

        self.led_ti_apply.set_channels2values(c2v)

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

    currentItem = Signal(str)
    itemDone = Signal(str)
    completed = Signal()
    sentWarning = Signal(str, list)

    def __init__(self, conn, cmds, warn_msgs=list(), parent=None,
                 use_log=False, size=None):
        """Initialize."""
        super().__init__(parent)
        self._quit_task = False

        self._cmds = cmds
        if not isinstance(self._cmds, list):
            self._cmds = [self._cmds, ]
        self._size = size if size is not None else len(self._cmds)

        self._warn_msgs = warn_msgs
        if not isinstance(self._warn_msgs, list):
            self._warn_msgs = [self._warn_msgs, ]

        self._conn = conn
        self._subsystem = self._get_subsystem()
        self._use_log = use_log
        if use_log:
            self._conn.logger = self

        self.sentWarning.connect(parent.show_warning_message)

    def size(self):
        """Task size."""
        return self._size

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def _get_subsystem(self):
        conn_name = self._conn.__class__.__name__
        if conn_name == 'ConnPS':
            return 'PS'
        elif conn_name == 'ConnTI':
            return 'TI'
        elif conn_name == 'ConnRF':
            return 'RF'

    def _verify_connector(self):
        if not self._conn:
            return False
        if not self._conn.connected:
            msg = 'There are not connected PVs in {}!'.format(self._subsystem)
            problems = self._conn.disconnected_properties
            self.sentWarning.emit(msg, problems)
            return False
        return True

    def run(self):
        """Run."""
        if not self._quit_task:
            if not self._verify_connector():
                return
            for cmd, msg in zip(self._cmds, self._warn_msgs):
                cmd_success, problems = cmd()
                if not cmd_success:
                    self.sentWarning.emit(msg, problems)
                if not self._use_log:
                    self.itemDone.emit('')
                if self._quit_task:
                    break
        if self._use_log:
            self._conn.logger = None
        self.completed.emit()

    def update(self, item):
        self.currentItem.emit(item)
        self.itemDone.emit(item)


class _createConnectorsThread(QThread):
    """Thread to create connectors and set leds channels."""

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.parent = parent
        self.prefix = prefix

    def run(self):
        # Create connectors
        self.parent.conn_ps = _ConnPS(prefix=self.prefix)
        self.parent.conn_ti = _ConnTI(prefix=self.prefix)
        self.parent.conn_rf = _ConnRF(prefix=self.prefix)

        # Build leds channels
        pfx = self.prefix

        # # Connection Leds
        for conn_name in ['conn_ps', 'conn_rf', 'conn_ti']:
            conn = getattr(self.parent, conn_name)
            c2v_conn = list()
            conn_type = conn.__class__.__name__.strip('Conn')
            for p in conn.properties:
                if conn_type == 'PS':
                    if 'PwrState' in conn[p].name:
                        c2v_conn.append(pfx + conn[p].pvname_rb)
                else:
                    c2v_conn.append(pfx + conn[p].pvname_rb)
            led_name = 'led_' + conn_type.lower() + '_conn'
            led = getattr(self.parent, led_name)
            led.set_channels(c2v_conn)

        # # PS
        conn = getattr(self.parent, 'conn_ps')
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
                c2v_apply[pfx + conn[p].pvname_sp.replace(
                    'Wfm-SP', 'WfmRef-Mon')] = None
        self.parent.led_ps_intlk.set_channels2values(c2v_intlk)
        self.parent.led_ps_setup.set_channels2values(c2v_setup)
        self.parent.led_ps_apply.set_channels2values(c2v_apply)

        # # RF
        conn = getattr(self.parent, 'conn_rf')
        c2v_intlk = dict()
        c2v_setup = dict()
        c2v_apply = dict()
        c2v_intlk[pfx + conn.Const.Rmp_Intlk] = 0
        c2v_setup[pfx + conn.Const.Rmp_RmpReady] = 1
        c2v_setup[pfx + conn.Const.Rmp_Enbl] = 1
        c2v_apply[pfx + conn.Const.Rmp_Ts1.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts2.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts3.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_Ts4.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_VoltBot.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_VoltTop.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_PhsBot.replace('SP', 'RB')] = None
        c2v_apply[pfx + conn.Const.Rmp_PhsTop.replace('SP', 'RB')] = None
        self.parent.led_rf_intlk.set_channels2values(c2v_intlk)
        self.parent.led_rf_setup.set_channels2values(c2v_setup)
        self.parent.led_rf_apply.set_channels2values(c2v_apply)

        # # TI
        conn = getattr(self.parent, 'conn_ti')
        c2v_intlk = dict()
        c2v_setup = dict()
        c2v_apply = dict()
        c2v_intlk[pfx + conn.Const.Intlk] = 0
        for prpty, value in conn.ramp_basicsetup.items():
            prpty = prpty.replace('SP', 'RB').replace('Sel', 'Sts')
            c2v_setup[pfx + prpty] = {'value': value, 'comp': 'cl',
                                      'abs_tol': 0.008}
        for prpty, value in conn.ramp_configsetup.items():
            prpty = prpty.replace('SP', 'RB')
            c2v_apply[pfx + prpty] = None
        self.parent.led_ti_intlk.set_channels2values(c2v_intlk)
        self.parent.led_ti_setup.set_channels2values(c2v_setup)
        self.parent.led_ti_apply.set_channels2values(c2v_apply)
