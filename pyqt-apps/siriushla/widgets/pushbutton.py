"""Sirius pushbutton."""

from qtpy.QtCore import Slot, Property

from pydm.widgets import PyDMPushButton


class SiriusPushButton(PyDMPushButton):
    """
    Basic PushButton to send a fixed value.

    The PyDMPushButton is meant to hold a specific value, and send that value
    to a channel when it is clicked, much like the MessageButton does in EDM.
    The PyDMPushButton works in two different modes of operation, first, a
    fixed value can be given to the :attr:`.pressValue` attribute, whenever the
    button is clicked a signal containing this value will be sent to the
    connected channel. This is the default behavior of the button. However, if
    the :attr:`.relativeChange` is set to True, the fixed value will be added
    to the current value of the channel. This means that the button will
    increment a channel by a fixed amount with every click, a consistent
    relative move

    Parameters
    ----------
    parent : QObject, optional
        Parent of PyDMPushButton

    init_channel : str, optional
        ID of channel to manipulate

    label : str, optional
        String to place on button

    icon : QIcon, optional
        An Icon to display on the PyDMPushButton

    pressValue : int, float, str
        Value to be sent when the button is pressed

    releaseValue : int, float, str
        Value to be sent when the button is released

    relative : bool, optional
        Choice to have the button perform a relative put, instead of always
        setting to an absolute value

    """

    def __init__(self, parent=None, init_channel=None, label='', icon=None,
                 pressValue=1, releaseValue=None, relative=False):
        PyDMPushButton.__init__(
            self, parent=parent, label=label, icon=icon,
            pressValue=pressValue, relative=relative,
            init_channel=init_channel)
        self._releaseValue = releaseValue
        self.clicked.disconnect(self.sendValue)
        self.pressed.connect(self.sendValue)
        self.released.connect(self.sendReleaseValue)

    @Property(str)
    def releaseValue(self):
        """
        This property holds the value to send back through the channel.

        The type of this value does not matter because it is automatically
        converted to match the prexisting value type of the channel. However,
        the sign of the value matters. Not used when relative flag is True.

        Returns
        -------
        str
        """
        if self._releaseValue is None:
            return None
        return str(self._releaseValue)

    @releaseValue.setter
    def releaseValue(self, value):
        """
        This property holds the value to send back through the channel.

        The type of this value does not matter because it is automatically
        converted to match the prexisting value type of the channel. However,
        the sign of the value matters. Not used when relative flag is True.

        Parameters
        ----------
        value : str
        """
        if value is None:
            self._releaseValue = None
        elif str(value) != self._releaseValue:
            self._releaseValue = str(value)

    @Slot()
    def sendReleaseValue(self):
        """
        Send a new value to the channel.

        This function interprets the settings of the PyDMPushButton and sends
        the appropriate value out through the :attr:`.send_value_signal`.

        Returns
        -------
        None if any of the following condition is False:
            1. There's no new value (pressValue) for the widget
            2. There's no initial or current value for the widget
            3. The relative flag is True
        Otherwise, return the value sent to the channel:
            1. The value sent to the channel is the same as the releaseValue
        """
        if self._releaseValue is None or self.value is None or self._relative:
            return None

        send_value = self._releaseValue
        self.send_value_signal[self.channeltype].emit(
            self.channeltype(send_value))
        return send_value
