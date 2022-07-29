"""Monitoring widgets."""

from qtpy.QtGui import QPixmap, QIcon
from qtpy.QtCore import Qt, Slot, Signal, QSize, QTimer
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, \
    QHBoxLayout, QCheckBox, QMenu, QFrame, QSizePolicy as QSzPol, \
    QPushButton

import qtawesome as qta

from pydm.widgets import PyDMPushButton
from pydm.connection_inspector import ConnectionInspector

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriuspy.devices import InjSysStandbyHandler, InjBOStandbyHandler
from siriuspy.clientarch import Time as _Time
from siriuspy.injctrl.csdev import get_status_labels, Const as _Const

from ..widgets import SiriusLedAlert, PyDMLedMultiChannel, PyDMLed, QLed, \
    SiriusConnectionSignal
from ..widgets.led import MultiChannelStatusDialog
from ..widgets.dialog import StatusDetailDialog


class MonitorSummaryWidget(QWidget):
    """Monitor Summary widget."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self._inj_dev = SiriusPVName('AS-Glob:AP-InjCtrl')
        self._inj_prefix = self._inj_dev.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        monitor = QGroupBox('Monitor')
        glay = QGridLayout(monitor)
        glay.setAlignment(Qt.AlignTop)
        glay.addWidget(QLabel('', self), 0, 0)

        sec_lbls = get_status_labels()
        for col, sec in enumerate(sec_lbls):
            lbl = QLabel(sec, self, alignment=Qt.AlignCenter)
            glay.addWidget(lbl, 0, col+1)
        sub_lbls = set()
        for sec in sec_lbls:
            sub_lbls.update(get_status_labels(sec))
        sub_lbls = sorted(sub_lbls)
        for row, sub in enumerate(sub_lbls):
            lbl = QLabel(sub, self, alignment=Qt.AlignCenter)
            glay.addWidget(lbl, row+1, 0)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        glay.addWidget(line, row+2, 0, 1, len(sec_lbls)+1)

        glay.addWidget(
            QLabel('All', self, alignment=Qt.AlignCenter), row+3, 0)

        for col, sec in enumerate(sec_lbls):
            lbls = get_status_labels(sec)
            for row, sub in enumerate(sub_lbls):
                if sub not in lbls:
                    continue
                bit = lbls.index(sub)
                led = SiriusLedAlert(
                    self, self._inj_prefix.substitute(
                        propty='DiagStatus'+sec+'-Mon'), bit=bit)
                glay.addWidget(led, row+1, col+1)

            bit = sec_lbls.index(sec)
            led = SiriusLedAlert(
                self, self._inj_prefix.substitute(
                    propty='DiagStatus-Mon'), bit=bit)
            glay.addWidget(led, row+3, col+1)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(monitor)


class InjDiagLed(SiriusLedAlert):
    """InjDiag Status Led."""

    def __init__(self, parent, prefix=VACA_PREFIX, **kws):
        init_channel = SiriusPVName(
            'AS-Glob:AP-InjCtrl:InjStatus-Mon').substitute(prefix=prefix)
        self.labels = get_status_labels('Inj')
        super().__init__(parent, init_channel, **kws)
        self.offColor = self.LightGreen
        self.onColor = self.Red

    def mouseDoubleClickEvent(self, event):
        """Reimplement mouseDoubleClickEvent."""
        if event.button() == Qt.LeftButton and self.labels:
            self.msg = StatusDetailDialog(
                parent=self.parent(), pvname=self.channel,
                labels=self.labels, title='Injection Status')
            self.msg.open()
        super().mouseDoubleClickEvent(event)


class InjSysStbyLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None, prefix=VACA_PREFIX, handler=None):
        if not handler:
            handler = InjSysStandbyHandler()
        super().__init__(parent, handler.on_values)
        self.stateColors = [PyDMLed.DarkGreen, PyDMLed.LightGreen,
                            PyDMLed.Yellow, PyDMLed.Gray]
        self._injbo_hdlr = InjBOStandbyHandler()
        self._injbo_onvals = self._injbo_hdlr.on_values
        self._ch_injmode = SiriusConnectionSignal(SiriusPVName(
            'AS-Glob:AP-InjCtrl').substitute(prefix=prefix, propty='Mode-Sts'))
        self._ch_injmode.new_value_signal[int].connect(
            self._handle_injmode_changed)

    def _update_statuses(self):
        if not self._connected:
            state = 3
        else:
            status_off = 0
            for status in self._address2status.values():
                if status == 'UNDEF' or not status:
                    status_off += 1
            if status_off == len(self._address2status.values()):
                state = 0
            elif status_off > 0:
                state = 2
            else:
                state = 1
        self.setState(state)

    def _handle_injmode_changed(self, new_mode):
        if new_mode == _Const.InjMode.TopUp:
            c2v = self.channels2values
            for key in self._injbo_onvals:
                c2v.pop(key)
            self.set_channels2values(c2v)
        elif new_mode == _Const.InjMode.Decay:
            c2v = self.channels2values
            for key, val in self._injbo_onvals.items():
                c2v[key] = val
            self.set_channels2values(c2v)

    def mouseDoubleClickEvent(self, ev):
        pv_groups, texts = list(), list()
        pvs_err, pvs_und = set(), set()
        for k, v in self._address2conn.items():
            if not v:
                pvs_und.add(k)
        if pvs_und:
            pv_groups.append(pvs_und)
            texts.append('There are disconnected PVs!')
        for k, v in self._address2status.items():
            if not v and k not in pvs_und:
                pvs_err.add(k)
        if pvs_err:
            pv_groups.append(pvs_err)
            texts.append(
                'The following PVs have value\n'
                'equivalent to off status!')

        if pv_groups:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pv_groups,
                text=texts, fun_show_diff=self._show_diff)
            msg.exec_()
        QLed.mouseDoubleClickEvent(self, ev)


class InjSysStbyControlWidget(QWidget):
    """Injection System Control Widget."""

    expand = Signal()

    def __init__(self, parent=None, prefix=VACA_PREFIX, is_summary=False,
                 handler=None):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self._inj_prefix = SiriusPVName(
            'AS-Glob:AP-InjCtrl').substitute(prefix=prefix)
        self._is_summary = is_summary
        self._last_comm = None

        self._handler = handler or InjSysStandbyHandler()
        self._icon_off = qta.icon('mdi.power-off')
        self._icon_on = qta.icon('mdi.power-on')
        self._icon_check = qta.icon('fa5s.check')
        self._pixmap_check = self._icon_check.pixmap(
            self._icon_check.actualSize(QSize(16, 16)))
        self._icon_not = qta.icon('fa5s.times')
        self._pixmap_not = self._icon_not.pixmap(
            self._icon_not.actualSize(QSize(16, 16)))

        self.menu = QMenu(self)
        self.rstord_act = self.menu.addAction('Reset Commands')
        self.rstord_act.triggered.connect(self._reset_commands_order)

        if is_summary:
            self._setupSummary()
        else:
            self._setupFull()

        self.conn_act = self.menu.addAction('Show Connections...')
        self.conn_act.triggered.connect(self._show_connections)

        self._ch_cmdsts = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='InjSysCmdSts-Mon'))

        self._ch_off_order_sp = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='InjSysTurnOffOrder-SP'))
        self._ch_off_order_rb = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='InjSysTurnOffOrder-RB'))
        self._ch_on_order_sp = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='InjSysTurnOnOrder-SP'))
        self._ch_on_order_rb = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='InjSysTurnOnOrder-RB'))
        if not is_summary:
            self._ch_cmdone = SiriusConnectionSignal(
                self._inj_prefix.substitute(propty='InjSysCmdDone-Mon'))

        self._ch_cmdsts.new_value_signal[int].connect(
            self._handle_cmdsts_buttons_enbl)
        self._ch_off_order_rb.new_value_signal[str].connect(
            self._handle_buttons_color)
        self._ch_on_order_rb.new_value_signal[str].connect(
            self._handle_buttons_color)
        self._ch_off_order_rb.new_value_signal[str].connect(
            self._handle_actions_state)
        self._ch_on_order_rb.new_value_signal[str].connect(
            self._handle_actions_state)
        if not is_summary:
            self._ch_cmdone.new_value_signal[str].connect(
                self._handle_cmdone_labels)
            self._ch_cmdsts.new_value_signal[int].connect(
                self._handle_cmdsts_labels)

    def _setupSummary(self):
        self._pb_off = PyDMPushButton(
            self, label='', icon=self._icon_off,
            init_channel=self._inj_prefix.substitute(
                propty='InjSysTurnOff-Cmd'),
            pressValue=0)
        self._pb_off.setObjectName('bt')
        self._pb_off.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_on = PyDMPushButton(
            self, label='', icon=self._icon_on,
            init_channel=self._inj_prefix.substitute(
                propty='InjSysTurnOn-Cmd'),
            pressValue=0)
        self._pb_on.setObjectName('bt')
        self._pb_on.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')

        self._led_sts = InjSysStbyLed(self, self.prefix)
        self._led_sts.setStyleSheet(
            'QLed{min-width:1.29em; max-width:1.29em;}')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._pb_off, 0, 0)
        lay.addWidget(self._pb_on, 0, 1)
        lay.addWidget(self._led_sts, 1, 0, 1, 2, alignment=Qt.AlignCenter)

        # menu
        for cmmtype in ['on', 'off']:
            order = getattr(self._handler, cmmtype+'_order')
            menu = QMenu('Select Turn '+cmmtype.upper()+' Commands', self)
            setattr(self, cmmtype+'_menu', menu)
            self.menu.addMenu(menu)
            for cmm in order:
                act = menu.addAction(self._handler.HANDLER_DESC[cmm])
                act.setObjectName(cmm)
                act.setCheckable(True)

    def _setupFull(self):
        lay = QGridLayout(self)

        lay.addWidget(QLabel('Off', self, alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(QLabel('On', self, alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel('Status', self, alignment=Qt.AlignCenter), 0, 3)

        self._checkbox_off = dict()
        self._checkbox_on = dict()
        self._labels_sts = dict()
        for idx, name in enumerate(self._handler.DEF_ON_ORDER):
            cb_off = QCheckBox(self)
            cb_off.setObjectName(name)
            self._checkbox_off[name] = cb_off
            cb_on = QCheckBox(self)
            cb_on.setObjectName(name)
            self._checkbox_on[name] = cb_on
            desc = self._handler.HANDLER_DESC[name]
            splitd = desc.split('(')
            lbl_txt = splitd[0]
            tip = ''
            if len(splitd) > 1:
                lbl_txt, tip = splitd
            lb_dsc = QLabel(lbl_txt, self, alignment=Qt.AlignLeft)
            if tip:
                lb_dsc.setToolTip(tip[:-1])
            lb_sts = QLabel('', self, alignment=Qt.AlignCenter)
            lb_sts.setObjectName(name)
            self._labels_sts[name] = lb_sts
            lay.addWidget(lb_dsc, idx+1, 0)
            lay.addWidget(cb_off, idx+1, 1, alignment=Qt.AlignCenter)
            lay.addWidget(cb_on, idx+1, 2, alignment=Qt.AlignCenter)
            lay.addWidget(lb_sts, idx+1, 3)

        self._pb_off = PyDMPushButton(
            self, label='', icon=self._icon_off,
            init_channel=self._inj_prefix.substitute(
                propty='InjSysTurnOff-Cmd'),
            pressValue=0)
        self._pb_off.setObjectName('bt')
        self._pb_off.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_on = PyDMPushButton(
            self, label='', icon=self._icon_on,
            init_channel=self._inj_prefix.substitute(
                propty='InjSysTurnOn-Cmd'),
            pressValue=0)
        self._pb_on.setObjectName('bt')
        self._pb_on.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')

        self._led_sts = InjSysStbyLed(self, self.prefix)

        lay.addWidget(self._pb_off, 6, 1)
        lay.addWidget(self._pb_on, 6, 2)
        lay.addWidget(self._led_sts, 6, 3)

    @Slot(int)
    def _handle_cmdsts_buttons_enbl(self, new_sts):
        if new_sts == _Const.InjSysCmdSts.On:
            self._pb_on.setEnabled(False)
            self._pb_on.setIcon(qta.icon(
                'fa5s.spinner', animation=qta.Spin(self._pb_on)))
            self._pb_off.setEnabled(False)
        elif new_sts == _Const.InjSysCmdSts.Off:
            self._pb_on.setEnabled(False)
            self._pb_off.setEnabled(False)
            self._pb_off.setIcon(qta.icon(
                'fa5s.spinner', animation=qta.Spin(self._pb_off)))
        else:
            if not self._pb_on.isEnabled():
                self._pb_on.setEnabled(True)
                self._pb_off.setEnabled(True)
                self._pb_on.setIcon(self._icon_on)
                self._pb_off.setIcon(self._icon_off)

    @Slot(str)
    def _handle_cmdone_labels(self, new_done):
        for name in self._handler.DEF_ON_ORDER:
            lbl = self._labels_sts[name]
            if name in new_done:
                lbl.setPixmap(self._pixmap_check)
            elif self._ch_cmdsts.value == _Const.InjSysCmdSts.Idle:
                lbl.setPixmap(self._pixmap_not)

    @Slot(int)
    def _handle_cmdsts_labels(self, new_sts):
        if new_sts == _Const.InjSysCmdSts.On:
            self._last_comm = new_sts
            for name in self._handler.DEF_ON_ORDER:
                if self._ch_on_order_rb.value is None:
                    break
                lbl = self._labels_sts[name]
                if name in self._ch_on_order_rb.value:
                    icon = qta.icon('fa5s.spinner')
                    pixmap = icon.pixmap(icon.actualSize(QSize(16, 16)))
                    lbl.setPixmap(pixmap)
                else:
                    lbl.setPixmap(QPixmap())
        elif new_sts == _Const.InjSysCmdSts.Off:
            self._last_comm = new_sts
            for name in self._handler.DEF_OFF_ORDER:
                if self._ch_off_order_rb.value is None:
                    break
                lbl = self._labels_sts[name]
                if name in self._ch_off_order_rb.value:
                    icon = qta.icon('fa5s.spinner')
                    pixmap = icon.pixmap(icon.actualSize(QSize(16, 16)))
                    lbl.setPixmap(pixmap)
                else:
                    lbl.setPixmap(QPixmap())
        else:
            done = self._ch_cmdone.value
            for name in self._handler.DEF_ON_ORDER:
                if done is None or name in done:
                    continue
                lbl = self._labels_sts[name]
                if self._last_comm == _Const.InjSysCmdSts.On and \
                        name in self._ch_on_order_rb.value:
                    lbl.setPixmap(self._pixmap_not)
                elif self._last_comm == _Const.InjSysCmdSts.Off and \
                        name in self._ch_off_order_rb.value:
                    lbl.setPixmap(self._pixmap_not)
            self._last_comm = None

    @Slot()
    def _set_commands_order(self):
        if self._is_summary:
            if self.sender() in self.on_menu.actions():
                on_order = [
                    a.objectName() for a in self.on_menu.actions()
                    if a.isChecked()]
                self._ch_on_order_sp.send_value_signal[str].emit(
                    ','.join(on_order))
            elif self.sender() in self.off_menu.actions():
                off_order = [
                    a.objectName() for a in self.off_menu.actions()
                    if a.isChecked()]
                self._ch_off_order_sp.send_value_signal[str].emit(
                    ','.join(off_order))
        else:
            if self.sender() in self._checkbox_on.values():
                checked = [
                    w.objectName() for w in self._checkbox_on.values()
                    if w.isChecked()]
                on_order = [
                    h for h in self._handler.DEF_ON_ORDER if h in checked]
                self._ch_on_order_sp.send_value_signal[str].emit(
                    ','.join(on_order))
            elif self.sender() in self._checkbox_off.values():
                checked = [
                    w.objectName() for w in self._checkbox_off.values()
                    if w.isChecked()]
                off_order = [
                    h for h in self._handler.DEF_OFF_ORDER if h in checked]
                self._ch_off_order_sp.send_value_signal[str].emit(
                    ','.join(off_order))

    @Slot()
    def _reset_commands_order(self):
        self._ch_off_order_sp.send_value_signal[str].emit(
            ','.join(self._handler.DEF_OFF_ORDER))
        self._ch_on_order_sp.send_value_signal[str].emit(
            ','.join(self._handler.DEF_ON_ORDER))
        if self._is_summary:
            for menu in [self.off_menu, self.on_menu]:
                for act in menu.actions():
                    act.toggled.disconnect()
                    act.setChecked(True)
                    act.toggled.connect(self._set_commands_order)
        else:
            for group in [self._checkbox_off, self._checkbox_on]:
                for wid in group.values():
                    wid.toggled.disconnect()
                    wid.setChecked(True)
                    wid.toggled.connect(self._set_commands_order)

    @Slot()
    def _handle_buttons_color(self):
        off_color = 'yellow' if self._ch_off_order_rb.value != \
            ','.join(self._handler.DEF_OFF_ORDER) else 'white'
        self._pb_off.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;'
            'background-color: '+off_color+';}')
        on_color = 'yellow' if self._ch_on_order_rb.value != \
            ','.join(self._handler.DEF_ON_ORDER) else 'white'
        self._pb_on.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;'
            'background-color: '+on_color+';}')

    @Slot(str)
    def _handle_actions_state(self, sts):
        state = 'on' if 'On' in self.sender().address else 'off'
        channel = getattr(self, '_ch_'+state+'_order_rb')
        if channel.value is None:
            return

        if self._is_summary:
            group = getattr(self, state+'_menu').actions()
        else:
            group = getattr(self, '_checkbox_'+state).values()
        for obj in group:
            obj.disconnect()
            ost = obj.objectName() in sts
            obj.setChecked(ost)
            obj.toggled.connect(self._set_commands_order)

    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        self.menu.popup(self.mapToGlobal(event.pos()))

    def _show_connections(self, checked):
        """Show connections action."""
        _ = checked
        conn = ConnectionInspector(self)
        conn.show()


class ClockLabel(QLabel):
    """Clock label."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update)
        self._update_timer.setInterval(1000)
        self._update_timer.start()

    def _update(self):
        text = _Time.strftime(_Time.now(), '%H:%M:%S')
        self.setText(text)


class TaskStatusLabel(QPushButton):
    """Label to show if task is running."""

    def __init__(self, parent=None, init_channel=None):
        super().__init__(parent)
        self._wait_icon = qta.icon('fa5s.spinner', animation=qta.Spin(self))
        self.setFlat(True)
        self._channel = SiriusConnectionSignal(init_channel)
        self._channel.new_value_signal[int].connect(self._update_icon)
        self.setSizePolicy(QSzPol.Fixed, QSzPol.Fixed)
        self.setMaximumSize(25, 25)
        self.setStyleSheet('QPushButton:hover{border:0pt solid transparent;}')

    def _update_icon(self, status):
        if status:
            self.setIcon(self._wait_icon)
        else:
            self.setIcon(QIcon())
