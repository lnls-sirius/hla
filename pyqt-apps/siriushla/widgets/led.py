from qtpy.QtGui import QColor
from qtpy.QtCore import Property
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

    def __init__(self, parent=None, init_channel='', bit=-1, color_list=None):
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
        value = int(new_val)
        if self._bit < 0:  # Led represents value of PV
            self.setState(value)
        else:  # Led represents specific bit of PV
            bit_val = (value & self._mask) >> self._bit
            self.setState(bit_val)


class SiriusLedState(PyDMLed):
    """PyDMLed specialization to represent 2 states in dark/light green."""

    def __init__(self, parent=None, init_channel='', bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOffColor(PyDMLed.DarkGreen)
        self.setOnColor(PyDMLed.LightGreen)


class SiriusLedAlert(PyDMLed):
    """PyDMLed specialization to represent 2 states in red/light green."""

    def __init__(self, parent=None, init_channel='', bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOnColor(PyDMLed.Red)
        self.setOffColor(PyDMLed.LightGreen)

    def value_changed(self, new_val):
        """If no bit is set, treat new_val as 2 states, zero and non-zero."""
        super().value_changed(int(new_val != 0) if self._bit < 0 else new_val)


class PyDMLedMultiChannel(QLed, PyDMWidget):
    """
    A QLed with support for checking values of several Channels.

    The led state notify if a set of PVs is in a desired state or not.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels_values_dict: dict
        A dict with channels as keys and desired PVs values as values.
    """

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen]

    def __init__(self, parent=None, channels2values=dict(),
                 color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.channels2values = channels2values
        self.stateColors = color_list or self.default_colorlist

        self.channels2ids = dict()
        for _id, channel in enumerate(sorted(self.channels2values.keys())):
            stid = str(_id)
            setattr(self, 'channel' + stid, channel)
            setattr(self, 'channel' + stid + '_value', None)
            setattr(self, 'channel' + stid + '_connected', False)
            self.channels2ids[channel] = stid

    def value_changed(self, new_val):
        """Receive new value and set led color accordingly."""
        if new_val is None:
            return
        channel = 'ca://' + self.sender().address
        setattr(self, 'channel'+self.channels2ids[channel]+'_value', new_val)
        state = 1
        for channel, desired_value in self.channels2values.items():
            val = getattr(self, 'channel'+self.channels2ids[channel]+'_value')
            state &= (val == desired_value)
        self.setState(state)

    def connectionStateChanged(self, conn):
        """Reimplement connectionStateChanged to handle all channels."""
        channel = 'ca://' + self.sender().address
        setattr(self, 'channel'+self.channels2ids[channel]+'_connected', conn)
        allconn = True
        for _id in self.channels2ids.values():
            allconn &= getattr(self, 'channel'+_id+'_connected')
        self.setEnabled(allconn)

    def channels(self):
        """
        Return the channels being used for this Widget.

        Returns
        -------
        channels : list
            List of PyDMChannel objects
        """
        if self._channels is None:
            self._channels = []
            for channel, _id in self.channels2ids.items():
                self._channels.append(
                    PyDMChannel(
                        address=channel,
                        connection_slot=self.connectionStateChanged,
                        value_slot=self.value_changed))
        return self._channels
