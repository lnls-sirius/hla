"""Standby widgets."""

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, \
    QMessageBox, QMenu, QAction, QGridLayout, QLabel
from qtpy.QtCore import Slot, Signal, QThread
import qtawesome as qta

from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, QLed
from siriushla.widgets.led import MultiChannelStatusDialog
from siriushla.widgets.dialog import PSStatusDialog
from .standby_handlers import PS_ENBL_VAL, PU_ENBL_VAL, PS_STS_RMPWFM, \
    LILLRF_ENBL_VAL,  BO_FAMS_EVT_INDEX, BO_CORRS_EVT_INDEX, \
    EVG_NAME, EVT_CONT_VAL, TRG_ENBL_VAL, \
    InjBOStandbyHandler, LILLRFStandbyHandler, PUStandbyHandler, \
    BOPSRampStandbyHandler, BORFRampStandbyHandler


CHANNELS_2_VALUES_MON = {
    # BO RF
    'BR-RF-DLLRF-01:RmpEnbl-Sts': TRG_ENBL_VAL,
    'BO-Glob:TI-LLRF-Rmp:State-Sts': TRG_ENBL_VAL,
    'BR-RF-DLLRF-01:RmpReady-Mon': TRG_ENBL_VAL,
    # InjBO event
    EVG_NAME+':InjBOMode-Sts': EVT_CONT_VAL,
}
# LI LLRF loop
for dev in LILLRFStandbyHandler.DEVICES:
    CHANNELS_2_VALUES_MON[dev + ':GET_INTEGRAL_ENABLE'] = LILLRF_ENBL_VAL
    CHANNELS_2_VALUES_MON[dev + ':GET_FB_MODE'] = LILLRF_ENBL_VAL
# BO PS
for dev in BOPSRampStandbyHandler.DEVICES:
    CHANNELS_2_VALUES_MON[dev+':OpMode-Sts'] = PS_STS_RMPWFM
    CHANNELS_2_VALUES_MON[dev+':WfmUpdateAuto-Sts'] = PS_ENBL_VAL
for trg in BOPSRampStandbyHandler.TRIGGERS:
    CHANNELS_2_VALUES_MON[trg+':State-Sel'] = TRG_ENBL_VAL
CHANNELS_2_VALUES_MON['BO-Glob:TI-Mags-Fams:Src-Sel'] = BO_FAMS_EVT_INDEX
CHANNELS_2_VALUES_MON['BO-Glob:TI-Mags-Corrs:Src-Sel'] = BO_CORRS_EVT_INDEX
# PU
for dev in PUStandbyHandler.DEVICES:
    if 'InjDpKckr' in dev:
        continue
    CHANNELS_2_VALUES_MON[dev+':Pulse-Sts'] = PU_ENBL_VAL
    CHANNELS_2_VALUES_MON[dev+':PwrState-Sts'] = PU_ENBL_VAL
for trg in PUStandbyHandler.TRIGGERS:
    CHANNELS_2_VALUES_MON[trg+':State-Sts'] = TRG_ENBL_VAL


class InjSysStandbyButton(PyDMWidget, QPushButton):
    """Button to set several PVs to standby state."""

    finished = Signal()

    def __init__(self, parent=None, label='', icon=None,
                 handlers=None, function=None, order=None):
        if not icon:
            QPushButton.__init__(self, label, parent)
        else:
            QPushButton.__init__(self, icon, label, parent)
        PyDMWidget.__init__(self)
        self.initial_icon = icon
        self._alarm_sensitive_border = False
        self._handlers = handlers
        self._function = function
        self._order = order
        self._address2conn = dict()
        for address in CHANNELS_2_VALUES_MON:
            self._address2conn[address] = False
            self._channel = address
            channel = PyDMChannel(
                address=self._channel,
                connection_slot=self.connectionStateChanged)
            channel.connect()
            self._channels.append(channel)

        self.pressed.connect(self._show_wait_icon)
        self.released.connect(self._start_send_thread)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = all(self._address2conn.values())
        self._connected = allconn
        self.check_enable_state()

    @Slot(list)
    def set_order(self, new_order):
        """Update order."""
        self._order = new_order

    def _show_wait_icon(self):
        """Show wait icon."""
        self.setIcon(
            qta.icon('fa5s.spinner', animation=qta.Spin(self)))

    def _show_init_icon(self):
        """Show initial icon."""
        self.setIcon(self.initial_icon)

    def _start_send_thread(self):
        if not self._connected:
            return

        thread = InjSysStandbySender(
            self._handlers, self._order, self._function, self)
        thread.sendWarning.connect(self._show_aux_message_box)
        thread.finished.connect(self._show_init_icon)
        thread.finished.connect(self.finished.emit)
        thread.start()

    def _show_aux_message_box(self, text, data_list):
        if 'PS' in text:
            dlg = PSStatusDialog(data_list, text, self)
        else:
            dlg = QMessageBox(self)
            dlg.setIcon(QMessageBox.Critical)
            dlg.setWindowTitle('Message')
            dlg.setText(text)
            details = ''
            for item in data_list:
                details += item + '\n'
            dlg.setDetailedText(details)
        dlg.exec_()


class InjSysStandbyEnblDsbl(QWidget):
    """Widget to control injection system standby state."""

    def __init__(self, handlers, on_order, off_order, parent=None):
        super().__init__(parent)
        self._handlers = handlers
        self._on_order = on_order
        self._off_order = off_order

        self.pb_off = InjSysStandbyButton(
            parent=self, icon=qta.icon('mdi.power-off'),
            handlers=self._handlers,
            function='turn_off', order=self._off_order)
        self.pb_off.setToolTip('Click to Turn Off')
        self.pb_off.setObjectName('pb_off')
        self.pb_off.setStyleSheet("""
            #pb_off{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)
        self.pb_off.released.connect(self._disable_commands)
        self.pb_off.finished.connect(self._enable_commands)

        self.pb_on = InjSysStandbyButton(
            parent=self, icon=qta.icon('mdi.power-on'),
            handlers=self._handlers,
            function='turn_on', order=self._on_order)
        self.pb_on.setToolTip('Click to Turn On')
        self.pb_on.setObjectName('pb_on')
        self.pb_on.setStyleSheet("""
            #pb_on{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)
        self.pb_on.released.connect(self._disable_commands)
        self.pb_on.finished.connect(self._enable_commands)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()

    def set_commands_order(self, new_on_order, new_off_order):
        if new_on_order != self._on_order:
            self.pb_on.set_order(new_on_order)
            self._on_order = new_on_order
        if new_off_order != self._off_order:
            self.pb_off.set_order(new_off_order)
            self._off_order = new_off_order

    def _disable_commands(self):
        self.pb_off.setEnabled(False)
        self.pb_on.setEnabled(False)

    def _enable_commands(self):
        self.pb_off.setEnabled(True)
        self.pb_on.setEnabled(True)


class InjSysStandbySender(QThread):
    """Thread to send Injection System Standby Mode."""

    sendWarning = Signal(str, list)

    def __init__(self, handlers, order, function, parent=None):
        """Initialize."""
        super().__init__(parent)
        self._handlers = handlers
        self._order = order
        self._function = function

    def run(self):
        """Run."""
        for handler_name in self._order:
            handler = self._handlers[handler_name]
            func = getattr(handler, self._function)
            retval = func()
            if not retval[0]:
                self.sendWarning.emit(retval[1], retval[2])
                break


class InjSysStandbyStatusLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None):
        super().__init__(parent, CHANNELS_2_VALUES_MON)
        self.stateColors = [PyDMLed.DarkGreen, PyDMLed.LightGreen,
                            PyDMLed.Yellow, PyDMLed.Gray]

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

    def mouseDoubleClickEvent(self, ev):
        pv_groups, texts = list(), list()
        pvs_err, pvs_und = set(), set()
        for k, v in self._address2status.items():
            if not v:
                pvs_err.add(k)
        if pvs_err:
            pv_groups.append(pvs_err)
            texts.append(
                'The following PVs have value\n'
                'equivalent to off status!')
        for k, v in self._address2conn.items():
            if not v:
                pvs_und.add(k)
        if pvs_und:
            pv_groups.append(pvs_und)
            texts.append('There are disconnected PVs!')

        if pv_groups:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pv_groups,
                text=texts, fun_show_diff=self._show_diff)
            msg.exec_()
        QLed.mouseDoubleClickEvent(self, ev)


class WidgetInjSys(QWidget):

    DEF_ON_ORDER = ['bo_rf', 'injbo', 'as_pu', 'bo_ps', 'li_rf']
    DEF_OFF_ORDER = ['li_rf', 'bo_rf', 'as_pu', 'bo_ps', 'injbo']
    COMM_DESC = {
        'as_pu': 'AS PU (Septa and Kickers)',
        'bo_ps': 'BO PS Ramp',
        'bo_rf': 'BO RF Ramp',
        'injbo': 'TI InjBO Event',
        'li_rf': 'LI LLRF (Klystrons Loop)',
    }

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._on_order = WidgetInjSys.DEF_ON_ORDER
        self._off_order = WidgetInjSys.DEF_OFF_ORDER
        self._handlers = {
            'as_pu': PUStandbyHandler(),
            'bo_ps': BOPSRampStandbyHandler(),
            'bo_rf': BORFRampStandbyHandler(),
            'injbo': InjBOStandbyHandler(),
            'li_rf': LILLRFStandbyHandler(),
        }

        self._but = InjSysStandbyEnblDsbl(
            self._handlers, self._on_order, self._off_order, self)
        self._led = InjSysStandbyStatusLed(self)

        # menu
        self.menu = QMenu(self)
        self.rstord_act = QAction('Reset Commands', self)
        self.rstord_act.triggered.connect(self._reset_commands_order)
        self.menu.addAction(self.rstord_act)
        for cmmtype in ['on', 'off']:
            order = getattr(self, '_'+cmmtype+'_order')
            menu = QMenu('Select Turn '+cmmtype.upper()+' Commands', self)
            setattr(self, cmmtype+'_menu', menu)
            self.menu.addMenu(menu)
            for cmm in order:
                act = QAction(WidgetInjSys.COMM_DESC[cmm], self)
                act.setObjectName(cmm)
                act.setCheckable(True)
                act.setChecked(True)
                act.toggled.connect(self._set_button_commands_order)
                menu.addAction(act)

        lay = QGridLayout(self)
        lay.setVerticalSpacing(5)
        lay.setHorizontalSpacing(15)
        lay.addWidget(QLabel('', self), 0, 1)
        lay.addWidget(self._but, 1, 0, 1, 3)
        lay.addWidget(self._led, 2, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(2, 2)

    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        self.menu.popup(self.mapToGlobal(event.pos()))

    def _set_button_commands_order(self):
        self._on_order = [
            a.objectName() for a in self.on_menu.actions() if a.isChecked()]
        self._off_order = [
            a.objectName() for a in self.off_menu.actions() if a.isChecked()]
        self._but.set_commands_order(self._on_order, self._off_order)
        if self._on_order != WidgetInjSys.DEF_ON_ORDER or \
                self._off_order != WidgetInjSys.DEF_OFF_ORDER:
            self._but.setStyleSheet('background-color: yellow;')
        else:
            self._but.setStyleSheet('background-color: white;')

    def _reset_commands_order(self):
        self._on_order = WidgetInjSys.DEF_ON_ORDER
        self._off_order = WidgetInjSys.DEF_OFF_ORDER
        for menu in [self.off_menu, self.on_menu]:
            for act in menu.actions():
                act.toggled.disconnect()
                act.setChecked(True)
                act.toggled.connect(self._set_button_commands_order)
        self._but.set_commands_order(self._on_order, self._off_order)
        self._but.setStyleSheet('background-color: white;')
