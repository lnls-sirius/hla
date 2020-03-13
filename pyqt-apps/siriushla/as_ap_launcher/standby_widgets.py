from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from qtpy.QtCore import Slot
import qtawesome as qta
from pydm.widgets.base import PyDMWidget, PyDMWritableWidget
from pydm.widgets.channel import PyDMChannel
from siriuspy.csdevice.timesys import Const as TIConst
from siriuspy.csdevice.pwrsupply import Const as PSConst
from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, QLed
from siriushla.widgets.led import MultiChannelStatusDialog


TRG_ENBL_VAL = TIConst.DsblEnbl.Enbl
TRG_DSBL_VAL = TIConst.DsblEnbl.Dsbl
PU_ENBL_VAL = PSConst.DsblEnbl.Enbl
PU_DSBL_VAL = PSConst.DsblEnbl.Dsbl

CHANNELS_2_VALUES = {
    'TB-04:PU-InjSept:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TB-04:PU-InjSept:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-01D:PU-InjKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-01D:PU-InjKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-48D:PU-EjeKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-48D:PU-EjeKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BR-RF-DLLRF-01:RmpEnbl-Sel': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-01:PU-EjeSeptF:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptF:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptG:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptG:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptF:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptF:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-1:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-1:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-2:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-2:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjNLKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjNLKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
}


class InjSysStandbyButton(PyDMWritableWidget, QPushButton):
    """Button to set several PVs to standby state."""

    def __init__(self, parent=None, label='', icon=None, pressValue=1):
        if not icon:
            QPushButton.__init__(self, label, parent)
        else:
            QPushButton.__init__(self, icon, label, parent)
        PyDMWritableWidget.__init__(self)
        self._alarm_sensitive_border = False
        self._pressvalue = pressValue
        self._address2values = dict()
        self._address2channel = dict()
        self._address2conn = dict()
        for address, values in CHANNELS_2_VALUES.items():
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_signal=self.send_value_signal)
            channel.connect()
            self._address2channel[address] = channel
            self._address2values[address] = values[pressValue]
        self.clicked.connect(self.sendValue)

    def sendValue(self):
        """Send values to PVs."""
        if not self._connected:
            return
        for addr, val in self._address2values.items():
            channel = self._address2channel[addr]
            channel.value_signal[int].emit(val)

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


class InjSysStandbyEnblDsbl(QWidget):
    """Widget to control injection system standby state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pb_off = InjSysStandbyButton(
            parent=self, pressValue=0,
            icon=qta.icon('mdi.power-off'))
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
            icon=qta.icon('mdi.power-on'))
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


class InjSysStandbyStatusLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None):
        channels2values = {k.replace('Sel', 'Sts'): v[1]
                           for k, v in CHANNELS_2_VALUES.items()}
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
