import time as _time

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox
from qtpy.QtCore import Slot, Signal
import qtawesome as qta

import pydm
from pydm.widgets.base import PyDMWidget, PyDMWritableWidget
from pydm.widgets.channel import PyDMChannel

from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, QLed
from siriushla.widgets.led import MultiChannelStatusDialog
from siriushla.widgets.dialog import PSStatusDialog
from .standby_handlers import TRG_ENBL_VAL, TRG_DSBL_VAL, \
    PU_ENBL_VAL, PU_DSBL_VAL, LILLRF_ENBL_VAL, LILLRF_DSBL_VAL, \
    PS_STS_SLWREF, PS_STS_RMPWFM, \
    BO_FAMS_EVT_INDEX, BO_CORRS_EVT_INDEX, \
    LILLRFStandbyHandler, BORampStandbyHandler


CHANNELS_2_VALUES_BUTTON = (
    # BO RF ramp enable
    ('BR-RF-DLLRF-01:RmpEnbl-Sel', (TRG_DSBL_VAL, TRG_ENBL_VAL)),
    # BO PS trigger
    ('BO-Glob:TI-Mags-Fams:State-Sel', (TRG_DSBL_VAL, TRG_ENBL_VAL)),
    ('BO-Glob:TI-Mags-Fams:Src-Sel', (None, BO_FAMS_EVT_INDEX)),
    ('BO-Glob:TI-Mags-Corrs:State-Sel', (TRG_DSBL_VAL, TRG_ENBL_VAL)),
    ('BO-Glob:TI-Mags-Corrs:Src-Sel', (None, BO_CORRS_EVT_INDEX)),
    # PU Pulse
    ('TB-04:PU-InjSept:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('BO-01D:PU-InjKckr:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('BO-48D:PU-EjeKckr:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-01:PU-EjeSeptF:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-01:PU-EjeSeptG:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptF:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptG-1:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptG-2:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('SI-01SA:PU-InjNLKckr:Pulse-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('SI-01SA:PU-InjDpKckr:Pulse-Sel', (PU_DSBL_VAL, None)),
    # PU PwrState
    ('TB-04:PU-InjSept:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('BO-01D:PU-InjKckr:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('BO-48D:PU-EjeKckr:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-01:PU-EjeSeptF:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-01:PU-EjeSeptG:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptF:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptG-1:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('TS-04:PU-InjSeptG-2:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('SI-01SA:PU-InjNLKckr:PwrState-Sel', (PU_DSBL_VAL, PU_ENBL_VAL)),
    ('SI-01SA:PU-InjDpKckr:PwrState-Sel', (PU_DSBL_VAL, None)),
)
CHANNELS_2_VALUES_LED = {pvn.replace('Sel', 'Sts'): vals
                         for pvn, vals in CHANNELS_2_VALUES_BUTTON}
CHANNELS_2_VALUES_LED.update({
    # PU triggers
    'TB-04:TI-InjSept:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-01:TI-EjeSeptF:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-01:TI-EjeSeptG:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptF:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptG-1:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptG-2:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'SI-01SA:TI-InjNLKckr:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    # BO RF trigger and ramp ready
    'BO-Glob:TI-LLRF-Rmp:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'BR-RF-DLLRF-01:RmpReady-Mon': (TRG_DSBL_VAL, TRG_ENBL_VAL),
})
# LI LLRF loop
for dev in LILLRFStandbyHandler.DEVICES:
    CHANNELS_2_VALUES_LED[dev + ':GET_INTEGRAL_ENABLE'] = \
        (LILLRF_DSBL_VAL, LILLRF_ENBL_VAL)
    CHANNELS_2_VALUES_LED[dev + ':GET_FB_MODE'] = \
        (LILLRF_DSBL_VAL, LILLRF_ENBL_VAL)
# BO PS opmode
for dev in BORampStandbyHandler.DEVICES:
    CHANNELS_2_VALUES_LED[dev+':OpMode-Sts'] = (PS_STS_SLWREF, PS_STS_RMPWFM)


class InjSysStandbyButton(PyDMWritableWidget, QPushButton):
    """Button to set several PVs to standby state."""

    willSend = Signal()
    justSent = Signal()

    def __init__(self, parent=None, label='', icon=None, pressValue=1,
                 linac_handler=None, booster_handler=None):
        if not icon:
            QPushButton.__init__(self, label, parent)
        else:
            QPushButton.__init__(self, icon, label, parent)
        PyDMWritableWidget.__init__(self)
        self.initial_icon = icon
        self._alarm_sensitive_border = False
        self._pressvalue = pressValue
        self._address2values = dict()
        self._address2channel = dict()
        self._address2conn = dict()
        for address, values in CHANNELS_2_VALUES_BUTTON:
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_signal=self.send_value_signal)
            channel.connect()
            self._address2channel[address] = channel
            self._address2values[address] = values[pressValue]
        self.pressed.connect(self.willSend.emit)
        self.released.connect(self.sendValue)

        self._linac_handler = linac_handler
        self._booster_handler = booster_handler

    def sendValue(self):
        """Send values to PVs."""
        if not self._connected:
            return

        if self._pressvalue == 1:
            retval = self._booster_handler.turn_on()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                self.justSent.emit()
                return

            retval = self._linac_handler.turn_on()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                self.justSent.emit()
                return

        for addr, val in self._address2values.items():
            if val is None:
                continue
            plugin = pydm.data_plugins.plugin_for_address(addr)
            conn = plugin.connections[addr]
            conn.put_value(val)

            timeout = 0.1 if 'PU' not in addr else 0.5 \
                if 'Pulse-Sel' in addr else 1
            _time.sleep(timeout)

        if self._pressvalue == 0:
            retval = self._booster_handler.turn_off()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                self.justSent.emit()
                return

            retval = self._linac_handler.turn_off()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                self.justSent.emit()
                return

        self.justSent.emit()

    @Slot(bool)
    def connection_changed(self, conn):
        """Handle connections."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        PyDMWidget.connection_changed(self, allconn)
        self._connected = allconn
        self.update()

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
        self._linac_handler = LILLRFStandbyHandler()
        self._booster_handler = BORampStandbyHandler()

        self.pb_off = InjSysStandbyButton(
            parent=self, pressValue=0,
            icon=qta.icon('mdi.power-off'),
            linac_handler=self._linac_handler,
            booster_handler=self._booster_handler)
        self.pb_off.willSend.connect(self.show_wait_icon)
        self.pb_off.justSent.connect(self.show_init_icon)
        self.pb_off.setToolTip('Click to Turn Off')
        self.pb_off.setObjectName('pb_off')
        self.pb_off.setStyleSheet("""
            #pb_off{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)
        self.pb_on = InjSysStandbyButton(
            parent=self, pressValue=1,
            icon=qta.icon('mdi.power-on'),
            linac_handler=self._linac_handler,
            booster_handler=self._booster_handler)
        self.pb_on.willSend.connect(self.show_wait_icon)
        self.pb_on.justSent.connect(self.show_init_icon)
        self.pb_on.setToolTip('Click to Turn On')
        self.pb_on.setObjectName('pb_on')
        self.pb_on.setStyleSheet("""
            #pb_on{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()

    def show_wait_icon(self):
        """Show wait icon."""
        self.sender().setIcon(qta.icon('fa5s.spinner', color='gray'))

    def show_init_icon(self):
        """Show init icon."""
        self.sender().setIcon(self.sender().initial_icon)


class InjSysStandbyStatusLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None):
        channels2values = {k: v[1] for k, v in CHANNELS_2_VALUES_LED.items()}
        super().__init__(parent, channels2values)
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
