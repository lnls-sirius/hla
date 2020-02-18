from qtpy.QtCore import Slot
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel
from siriuspy.csdevice.timesys import Const as TIConst
from siriuspy.csdevice.pwrsupply import Const as PSConst
from siriushla.widgets import PyDMStateButton, PyDMLedMultiChannel, PyDMLed


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
    'SI-01SA:PU-InjDpKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjDpKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
}


class InjSysStandbyButton(PyDMStateButton):
    """Button to set several PVs to standby state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._address2values = dict()
        self._address2channel = dict()
        self._address2conn = dict()
        self._address2currvals = dict()
        for address, value in CHANNELS_2_VALUES.items():
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_slot=self.value_changed,
                value_signal=self.send_value_signal)
            channel.connect()
            self._address2channel[address] = channel
            self._address2values[address] = value
            self._address2currvals[address] = 'UNDEF'

    @Slot(int)
    def value_changed(self, new_val):
        """Reimplement value_changed."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2currvals[address] = new_val
        button_val = all(self._address2currvals.values())
        super(PyDMStateButton, self).value_changed(button_val)
        self.value = button_val
        self._bit_val = button_val
        self.update()

    def send_value(self):
        """Reimplement send_value."""
        if not self._connected:
            return
        new_val = not self.value
        for addr, val in self._address2values.items():
            val_2_send = self._address2values[addr][new_val]
            channel = self._address2channel[addr]
            channel.value_signal[int].emit(val_2_send)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed."""
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


class InjSysStandbyStatusLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None):
        channels2values = {k.replace('Sel', 'Sts'): v[1]
                           for k, v in CHANNELS_2_VALUES.items()}
        super().__init__(parent, channels2values)
        self.offColor = PyDMLed.DarkGreen
