from copy import deepcopy as _dcopy
import logging as _log
import numpy as _np
from qtpy.QtGui import QColor
from qtpy.QtCore import Property, Slot, Signal
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel
from .QLed import QLed


class PyDMLed(QLed, PyDMWidget):
    """
    A QLed with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    init_channel : str, optional
        The channel to be used by the widget.
    bit : int
        Bit of the PV value to be handled.
    color_list : int
        List of QColor objects for each state the channel can assume.
    """

    DarkGreen = QColor(20, 80, 10)
    LightGreen = QColor(0, 140, 0)
    Yellow = QColor(210, 205, 0)
    Red = QColor(207, 0, 0)
    default_colorlist = [DarkGreen, LightGreen, Yellow, Red]

    def __init__(self, parent=None, init_channel=None, bit=-1,
                 color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.pvbit = bit
        self.stateColors = color_list or self.default_colorlist

    @Property(int)
    def pvbit(self):
        """PV bit to be handled by the led."""
        return self._bit

    @pvbit.setter
    def pvbit(self, bit):
        if bit >= 0:
            self._bit = int(bit)
            self._mask = 1 << bit
        else:
            self._bit = -1
            self._mask = None

    def value_changed(self, new_val):
        """
        Receive new value and set led color accordingly.

        For int or float data type the standard led behaviour is to be red when
        the value is 0, and green otherwise.

        If a :attr:`bit` is set the value received will be treated as an int
        and the bit value is extracted using a mask. The led represents the
        value of the chosen bit.
        """
        PyDMWidget.value_changed(self, new_val)
        if new_val is None:
            return
        if isinstance(new_val, _np.ndarray):
            _log.warning('PyDMLed received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        value = int(new_val)
        if self._bit < 0:  # Led represents value of PV
            self.setState(value)
        else:  # Led represents specific bit of PV
            bit_val = (value & self._mask) >> self._bit
            self.setState(bit_val)


class SiriusLedState(PyDMLed):
    """PyDMLed specialization to represent 2 states in dark/light green."""

    def __init__(self, parent=None, init_channel=None, bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOffColor(PyDMLed.DarkGreen)
        self.setOnColor(PyDMLed.LightGreen)

    def value_changed(self, new_val):
        """Reimplement value_changed to filter bug."""
        if isinstance(new_val, _np.ndarray):
            _log.warning('SiriusLedState received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        super().value_changed(new_val)


class SiriusLedAlert(PyDMLed):
    """PyDMLed specialization to represent 2 states in red/light green."""

    def __init__(self, parent=None, init_channel=None, bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOnColor(PyDMLed.Red)
        self.setOffColor(PyDMLed.LightGreen)

    def value_changed(self, new_val):
        """If no bit is set, treat new_val as 2 states, zero and non-zero."""
        if isinstance(new_val, _np.ndarray):
            _log.warning('SiriusLedAlert received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        value = int(new_val != 0) if self._bit < 0 else new_val
        super().value_changed(value)


class PyDMLedMultiChannel(QLed, PyDMWidget):
    """
    A QLed with support for checking values of several Channels.

    The led state notify if a set of PVs is in a desired state or not.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels2values: dict
        A dict with channels as keys and desired PVs values as values.
        Values can be either a scalar, to simple comparision, or a dict.
        This dict can have as keys:
            - 'value' (the value to use in comparision);
            - 'comp' (a string that select the type of comparision, can be
                      'eq', 'ne', 'gt', 'lt', 'ge', 'le');
            - and 'bit' (select a bit of the pv to compare to 'value').
    """

    warning = Signal(list)
    normal = Signal(list)

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen]

    def __init__(self, parent=None, channels2values=dict(), color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.stateColors = _dcopy(color_list) or self.default_colorlist

        self._operations_dict = {'eq': self._eq,
                                 'ne': self._ne,
                                 'gt': self._gt,
                                 'lt': self._lt,
                                 'ge': self._ge,
                                 'le': self._le}

        self._address2conn = dict()
        self._address2channel = dict()
        self._address2status = dict()
        self.set_channels2values(_dcopy(channels2values))

    @property
    def channels2values(self):
        return _dcopy(self._address2values)

    @property
    def channels2status(self):
        return _dcopy(self._address2status)

    def set_channels2values(self, new_channels2values):
        self._address2values = new_channels2values

        if not new_channels2values:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        # Check which channel can be removed
        address2pop = list()
        for address in self._address2channel.keys():
            if address not in new_channels2values.keys():
                address2pop.append(address)

        # Remove channels
        for address in address2pop:
            self._address2channel[address].disconnect()
            self._address2channel.pop(address)
            self._address2status.pop(address)
            self._address2conn.pop(address)

        # Add new channels
        for address, value in new_channels2values.items():
            if address not in self._address2channel.keys():
                self._address2conn[address] = False
                self._address2status[address] = 'UNDEF'
                channel = PyDMChannel(
                    address=address,
                    connection_slot=self.connection_changed,
                    value_slot=self.value_changed)
                channel.connect()
                self._address2channel[address] = channel
            self._address2values[address] = value

        self._channels = list(self._address2channel.values())

        self._update_statuses()

    def value_changed(self, new_val):
        """Receive new value and set led color accordingly."""
        if not self.sender():   # do nothing when sender None
            return
        address = self.sender().address
        desired = self._address2values[address]

        if isinstance(desired, dict):
            if 'bit' in desired.keys():
                bit = desired['bit']
                mask = 1 << bit
                new_val = (new_val & mask) >> bit
            if 'comp' in desired.keys():
                fun = self._operations_dict[desired['comp']]
            else:
                fun = self._operations_dict['eq']
            desired_value = desired['value']
        else:
            fun = self._operations_dict['eq']
            desired_value = desired
        if (type(new_val) != type(desired_value)) \
                and isinstance(new_val, _np.ndarray):
            _log.warning('PyDMLedMultiChannel received a numpy array to ' +
                         address+' ('+str(new_val)+')!')
            return

        is_desired = fun(new_val, desired_value)
        self._address2status[address] = is_desired
        if not is_desired:
            self.warning.emit([address, new_val])
        else:
            self.normal.emit([address, new_val])
        self._update_statuses()

    def _update_statuses(self):
        state = True
        for status in self._address2status.values():
            if status == 'UNDEF':
                state = False
                break
            state &= status
        self.setState(state)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        PyDMWidget.connection_changed(self, allconn)
        self.setEnabled(allconn)

    @staticmethod
    def _eq(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_equal = _np.all(val1 == val2)
        else:
            is_equal = (val1 == val2)
        return is_equal

    @staticmethod
    def _ne(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_not_equal = _np.all(val1 != val2)
        else:
            is_not_equal = (val1 != val2)
        return is_not_equal

    @staticmethod
    def _gt(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_greater = _np.all(val1 > val2)
        else:
            is_greater = (val1 > val2)
        return is_greater

    @staticmethod
    def _lt(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_less = _np.all(val1 < val2)
        else:
            is_less = (val1 < val2)
        return is_less

    @staticmethod
    def _ge(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_greater_or_equal = _np.all(val1 >= val2)
        else:
            is_greater_or_equal = (val1 >= val2)
        return is_greater_or_equal

    @staticmethod
    def _le(val1, val2):
        if val1 is None or val2 is None:
            return False
        if isinstance(val1, _np.ndarray):
            is_less_or_equal = _np.all(val1 <= val2)
        else:
            is_less_or_equal = (val1 <= val2)
        return is_less_or_equal


class PyDMLedMultiConnection(QLed, PyDMWidget):
    """
    A QLed with support for checking connection of several Channels.

    The led state notify if a set of PVs is connected.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels: list
        A list of channels.
    """

    warning = Signal(list)
    normal = Signal(list)

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen]

    def __init__(self, parent=None, channels=list(), color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.stateColors = color_list or self.default_colorlist

        self._address2conn = dict()
        self._address2channel = dict()
        self.set_channels(channels)

    @property
    def channels2conn(self):
        """Return dict with connection state of each channel."""
        return _dcopy(self._address2conn)

    def set_channels(self, new_channels):
        if not new_channels:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        # Check which channel can be removed
        address2pop = list()
        for address in self._address2channel.keys():
            if address not in new_channels:
                address2pop.append(address)
            else:
                new_channels.remove(address)

        # Remove channels
        for address in address2pop:
            self._address2channel[address].disconnect()
            self._address2channel.pop(address)
            self._address2conn.pop(address)

        # Add new channels
        for address in new_channels:
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address, connection_slot=self.connection_changed)
            channel.connect()
            self._address2channel[address] = channel

        self._channels = list(self._address2channel.values())

        self._update_state()

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender None
            return
        address = self.sender().address
        if not conn:
            self.warning.emit([address, conn])
        else:
            self.normal.emit([address, conn])
        self._address2conn[address] = conn
        self._update_state()

    def _update_state(self):
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        self.setState(allconn)
        self._connected = allconn
