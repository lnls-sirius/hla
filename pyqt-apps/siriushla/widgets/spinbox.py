from qtpy.QtCore import Property
from pydm.widgets import PyDMSpinbox
from pydm.widgets.base import PyDMWritableWidget


class SiriusSpinbox(PyDMSpinbox):
    """
    A QDoubleSpinBox with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """
    def __init__(self, parent=None, init_channel=None):
        super(SiriusSpinbox, self).__init__(parent, init_channel)
        self._limits_from_channel = True
        self._user_lower_limit = self.minimum()
        self._user_upper_limit = self.maximum()

    def ctrl_limit_changed(self, which, new_limit):
        """
        Callback invoked when the Channel receives new control limit
        values.

        Parameters
        ----------
        which : str
            Which control limit was changed. "UPPER" or "LOWER"
        new_limit : float
            New value for the control limit
        """
        PyDMWritableWidget.ctrl_limit_changed(self, which, new_limit)
        self.update_limits()

    def update_limits(self):
        """
        Callback invoked to update the control limits of the spinbox.

        Parameters
        ----------
        which : str
            Which control limit was changed. "UPPER" or "LOWER"
        new_limit : float
            New value for the control limit
        """
        if self._limits_from_channel:
            if self._lower_ctrl_limit is not None:
                super(SiriusSpinbox, self).setMinimum(self._lower_ctrl_limit)
            if self._upper_ctrl_limit is not None:
                super(SiriusSpinbox, self).setMaximum(self._upper_ctrl_limit)
        else:
            super(SiriusSpinbox, self).setMinimum(self._user_lower_limit)
            super(SiriusSpinbox, self).setMaximum(self._user_upper_limit)

    def precision_changed(self, new_precision):
        """
        Callback invoked when the Channel has new precision value.
        This callback also triggers an update_format_string call so the
        new precision value is considered.

        Parameters
        ----------
        new_precison : int or float
            The new precision value
        """
        super(SiriusSpinbox, self).precision_changed(new_precision)
        self.update_limits()

    @Property(bool)
    def limitsFromChannel(self):
        """
        A choice whether or not to use the limits given by channel.

        Returns
        -------
        limits_from_channel : bool
            True means that the widget will use the limits information
            from the Channel if available.
        """
        return self._limits_from_channel

    @limitsFromChannel.setter
    def limitsFromChannel(self, value):
        """
        A choice whether or not to use the limits given by channel.

        Parameters
        ----------
        value : bool
            True means that the widget will use the limits information
            from the PV if available.
        """
        if self._limits_from_channel != bool(value):
            self._limits_from_channel = bool(value)
            self.update_limits()

    def setMinimum(self, value):
        """
        Set the user defined lower limit for the spinbox.

        Parameters
        ----------
        value : float
            The new lower limit value.
        """
        self._user_lower_limit = float(value)
        self._user_upper_limit = max(
            self._user_upper_limit, self._user_lower_limit)
        self.update_limits()

    def setMaximum(self, value):
        """
        Set the user defined upper limit for the spinbox.

        Parameters
        ----------
        value : float
            The new upper limit value.
        """
        self._user_upper_limit = float(value)
        self._user_lower_limit = min(
            self._user_lower_limit, self._user_upper_limit)
        self.update_limits()

    def setRange(self, mini, maxi):
        """
        Set the user defined limits for the spinbox.

        Parameters
        ----------
        mini : float
            The new lower limit value.
        maxi: float
            The new upper limit value.
        """
        self.setMinimum(mini)
        self.setMaximum(maxi)

    def get_user_limits(self):
        """
        Get the user defined limits for the spinbox.

        Returns
        ----------
        limits: tuple
            2-tuple with the user defined minimum and maximum.
        """
        return (self._user_lower_limit, self._user_upper_limit)
