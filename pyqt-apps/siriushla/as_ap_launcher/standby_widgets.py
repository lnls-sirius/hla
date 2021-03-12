"""Standby widgets."""

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._handlers = {
            'injbo': InjBOStandbyHandler(),
            'li_rf': LILLRFStandbyHandler(),
            'as_pu': PUStandbyHandler(),
            'bo_ps': BOPSRampStandbyHandler(),
            'bo_rf': BORFRampStandbyHandler(),
        }
        self._off_order = ['li_rf', 'bo_rf', 'as_pu', 'bo_ps', 'injbo']
        self._on_order = ['bo_rf', 'injbo', 'as_pu', 'bo_ps', 'li_rf']

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
        pvs = set()
        for k, v in self._address2status.items():
            if (not v) or (v == 'UNDEF'):
                pvs.add(k)
        if pvs:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pvs,
                text="The following PVs have value\n"
                     "equivalent to 'off' status!",
                fun_show_diff=self._show_diff)
            msg.exec_()
        QLed.mouseDoubleClickEvent(self, ev)
