import datetime as _datetime
from pydm.PyQt.QtGui import QListWidget
from pydm.PyQt.QtCore import pyqtProperty
from pydm.widgets.base import PyDMWidget


class PyDMLogLabel(QListWidget, PyDMWidget):
    """
    A QListWidget with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    def __init__(self, parent=None, init_channel=None):
        QListWidget.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self._buffer_size = 1000
        self._prepend_date_time = True
        self._date_time_fmt = '%Y/%M/%d-%H:%M:%S'

    def value_changed(self, new_value):
        """
        Callback invoked when the Channel value is changed.

        Sets the value of new_value accordingly at the Label.

        Parameters
        ----------
        new_value : str, int, float, bool or np.ndarray
            The new value from the channel. The type depends on the channel.
        """
        super(PyDMLogLabel, self).value_changed(new_value)

        if self.count() > self._buffer_size:
            self.clear()

        prefix = ''
        if self._prepend_date_time:
            prefix += _datetime.datetime.now().strftime(self._date_time_fmt)
            prefix += ' '
        # If the value is a string, just display it as-is, no formatting
        # needed.
        if isinstance(new_value, str):
            self.addItem(prefix + new_value)
            return
        # If the value is an enum, display the appropriate enum string for
        # the value.
        if self.enum_strings is not None and isinstance(new_value, int):
            try:
                self.addItem(prefix + self.enum_strings[new_value])
            except IndexError:
                self.addItem("**INVALID**")
            return
        # If the value is a number (float or int), display it using a
        # format string if necessary.
        if isinstance(new_value, (int, float)):
            self.addItem(prefix + self.format_string.format(new_value))
            return
        # If you made it this far, just turn whatever the heck the value
        # is into a string and display it.
        self.addItem(prefix + str(new_value))

    @pyqtProperty(int)
    def bufferSize(self):
        """
        The maximum number of entries to show.

        When maximum is exceeded the widget is cleared.

        Returns
        -------
        int
        """
        return int(self._buffer_size)

    @bufferSize.setter
    def bufferSize(self, value):
        """
        The maximum number of entries to show.

        When maximum is exceeded the widget is cleared.

        Parameters
        ----------
        value : int
        """
        self._buffer_size = int(value)

    @pyqtProperty(bool)
    def prependDateTime(self):
        """
        Define if the date and time information will be prepended to the text.

        Returns
        -------
        bool
        """
        return self._prepend_date_time

    @prependDateTime.setter
    def prependDateTime(self, value):
        """
        Define if the date and time information will be prepended to the text.

        Parameters
        ----------
        value : bool
        """
        self._prepend_date_time = bool(value)

    @pyqtProperty(str)
    def dateTimeFmt(self):
        """
        Define the format of the datetime information to be prepended.

        Returns
        -------
        str
        """
        return self._date_time_fmt

    @dateTimeFmt.setter
    def dateTimeFmt(self, value):
        """
        Define the format of the datetime information to be prepended.

        Parameters
        ----------
        value : str
        """
        self._date_time_fmt = str(value)
