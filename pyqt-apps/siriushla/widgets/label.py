from pyqtgraph import functions as func
from qtpy.QtWidgets import QLabel, QApplication
from qtpy.QtCore import Qt, Property, Q_ENUMS
from pydm.utilities import units
from pydm.widgets.display_format import DisplayFormat, parse_value_for_display
from pydm.widgets.base import PyDMWidget, TextFormatter
from pydm.utilities import is_pydm_app


class SiriusLabel(QLabel, TextFormatter, PyDMWidget, DisplayFormat):
    Q_ENUMS(DisplayFormat)
    DisplayFormat = DisplayFormat
    """
    A QLabel with support for Channels and more from PyDM

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    def __init__(self, parent=None, init_channel=None, **kws):
        QLabel.__init__(self, parent, **kws)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.app = QApplication.instance()
        self.setTextFormat(Qt.PlainText)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setText("PyDMLabel")
        self._display_format_type = self.DisplayFormat.Default
        self._string_encoding = "utf_8"
        self._conv = 1
        if is_pydm_app():
            self._string_encoding = self.app.get_string_encoding()

    @Property(DisplayFormat)
    def displayFormat(self):
        return self._display_format_type

    @displayFormat.setter
    def displayFormat(self, new_type):
        if self._display_format_type != new_type:
            self._display_format_type = new_type
            # Trigger the update of display format
            self.value_changed(self.value)

    def update_format_string(self):
        """
        Reconstruct the format string to be used when representing the
        output value.

        Returns
        -------
        format_string : str
            The format string to be used including or not the precision
            and unit
        """
        self.format_string = "{}"
        if isinstance(self.value, (int, float)):
            self.format_string = "{:." + str(self.precision) + "f}"
        if self._show_units and self._unit != "":
            unt_opt = units.find_unit_options(self._unit)
            if unt_opt:
                unt_si = [un for un in unt_opt if units.find_unit(un) == 1][0]
                self._conv = units.convert(self._unit, unt_si)
            else:
                self._conv = 1
                unt_si = self._unit
            self.format_string += " {}"+"{}".format(unt_si)
        return self.format_string

    def value_changed(self, new_value):
        """
        Callback invoked when the Channel value is changed.
        Sets the value of new_value accordingly at the Label.

        Parameters
        ----------
        new_value : str, int, float, bool or np.ndarray
            The new value from the channel. The type depends on the channel.
        """
        super(SiriusLabel, self).value_changed(new_value)
        new_value = parse_value_for_display(
            value=new_value, precision=self.precision,
            display_format_type=self._display_format_type,
            string_encoding=self._string_encoding, widget=self)
        # If the value is a string, just display it as-is, no formatting
        # needed.
        if isinstance(new_value, str):
            self.setText(new_value)
            return
        # If the value is an enum, display the appropriate enum string for
        # the value.
        if self.enum_strings and isinstance(new_value, (int, float)):
            try:
                self.setText(self.enum_strings[int(new_value)])
            except IndexError:
                self.setText("**INVALID**")
            return
        # If the value is a number (float or int), display it using a
        # format string if necessary.
        if isinstance(new_value, (int, float)):
            if self._show_units and self._unit != '':
                new_value *= self._conv
                sc, prf = func.siScale(new_value)
                self.setText(self.format_string.format(sc*new_value, prf))
            else:
                self.setText(self.format_string.format(new_value))
            return
        # If you made it this far, just turn whatever the heck the value
        # is into a string and display it.
        self.setText(str(new_value))
