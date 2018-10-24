import datetime as _datetime
from qtpy.QtWidgets import QListWidget, QListWidgetItem
from qtpy.QtCore import Property, Q_ENUMS
from qtpy.QtGui import QColor
from pydm.widgets.base import PyDMWidget
from pydm.widgets.display_format import DisplayFormat, parse_value_for_display


class PyDMLogLabel(QListWidget, PyDMWidget, DisplayFormat):
    """
    A QListWidget with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    DisplayFormat = DisplayFormat
    Q_ENUMS(DisplayFormat)

    errorcolor = QColor(255, 0, 0)
    warncolor = QColor(200, 200, 0)

    def __init__(self, parent=None, init_channel=None):
        QListWidget.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self._buffer_size = 1000
        self._prepend_date_time = True
        self._display_format_type = DisplayFormat.String
        self._string_encoding = "utf_8"
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

        new_value = parse_value_for_display(
            value=new_value,
            precision=self._prec,
            display_format_type=self._display_format_type,
            string_encoding=self._string_encoding,
            widget=self)

        if self.count() > self._buffer_size:
            self.clear()

        prefix = ''
        if self._prepend_date_time:
            prefix += _datetime.datetime.now().strftime(self._date_time_fmt)
            prefix += ' '
        # If the value is a string, just display it as-is, no formatting
        # needed.
        item = None
        if isinstance(new_value, str):
            item = QListWidgetItem(prefix + new_value)
            if new_value.lower().startswith(('err', 'fatal')):
                item.setForeground(self.errorcolor)
            elif new_value.lower().startswith('warn'):
                item.setForeground(self.warncolor)
        # If the value is an enum, display the appropriate enum string for
        # the value.
        elif self.enum_strings is not None and isinstance(new_value, int):
            try:
                item = QListWidgetItem(prefix + self.enum_strings[new_value])
            except IndexError:
                item = QListWidgetItem("**INVALID**")
        # If the value is a number (float or int), display it using a
        # format string if necessary.
        elif isinstance(new_value, (int, float)):
            item = QListWidgetItem(prefix+self.format_string.format(new_value))
        # If you made it this far, just turn whatever the heck the value
        # is into a string and display it.
        else:
            item = QListWidgetItem(prefix + str(new_value))

        if item is not None:
            self.addItem(item)

    @Property(DisplayFormat)
    def displayFormat(self):
        """
        The format to display data.

        Returns
        -------
        int
        """
        return self._display_format_type

    @displayFormat.setter
    def displayFormat(self, new_type):
        """
        The maximum number of entries to show.

        When maximum is exceeded the widget is cleared.

        Returns
        -------
        int
        """
        if self._display_format_type != new_type:
            self._display_format_type = new_type
            # Trigger the update of display format
            self.value_changed(self.value)

    @Property(int)
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

    @Property(bool)
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

    @Property(str)
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
