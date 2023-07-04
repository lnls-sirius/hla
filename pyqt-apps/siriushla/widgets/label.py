"""Sirius Label."""

from pyqtgraph import functions as func
from qtpy.QtWidgets import QLabel, QApplication
from qtpy.QtCore import Qt, Property, Q_ENUMS
from pydm.utilities import units
from pydm.widgets.base import PyDMPrimitiveWidget
from pydm.widgets.display_format import DisplayFormat, parse_value_for_display
from pydm.widgets.base import PyDMWidget, TextFormatter
from pydm.utilities import is_pydm_app, is_qt_designer

from siriuspy.clientarch import Time as _Time


class SiriusLabel(QLabel, TextFormatter, PyDMWidget, DisplayFormat):
    """
    A QLabel with support for Channels and more from PyDM

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    keep_unit : bool, optional
        If True, label do not use unit convertion feature.
        Default to False.
    """
    Q_ENUMS(DisplayFormat)
    DisplayFormat = DisplayFormat
    DisplayFormat.Time = 6
    DisplayFormat.BSMPUDCVersion = 7
    DisplayFormat.TIFRMVersion = 8

    def __init__(self, parent=None, init_channel=None, keep_unit=False, **kws):
        """Init."""
        QLabel.__init__(self, parent, **kws)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.app = QApplication.instance()
        self.setTextFormat(Qt.PlainText)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setText("######")
        self._display_format_type = self.DisplayFormat.Default
        self._string_encoding = "utf_8"
        self._conv = 1
        self._keep_unit = keep_unit
        if is_pydm_app():
            self._string_encoding = self.app.get_string_encoding()

    @Property(DisplayFormat)
    def displayFormat(self):
        """Display Format."""
        return self._display_format_type

    @displayFormat.setter
    def displayFormat(self, new_type):
        if self._display_format_type == new_type:
            return
        self._display_format_type = new_type
        if not is_qt_designer():
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
            if self._keep_unit:
                self.format_string += " {}".format(self._unit)
            else:
                unt_opt = units.find_unit_options(self._unit)
                if unt_opt:
                    unt_si = [u for u in unt_opt if units.find_unit(u) == 1][0]
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
        # If it is a DiaplayFormat.Time, parse with siriuspy.clientarch.Time
        if self._display_format_type == self.DisplayFormat.Time:
            time = _Time(int(new_value)).time().isoformat() \
                if new_value is not None else ''
            self.setText(time)
            return

        # If it is a version string, replace multiple whitespaces with a
        # single one
        if self._display_format_type == self.DisplayFormat.BSMPUDCVersion:
            version = new_value[:16] + " " + new_value[16:] \
                if new_value is not None else ''
            version = " ".join(version.split())
            self.setText(version)
            return

        # If it is a TI Frm. version string, convert to unsigned int and
        # represent in hex
        if self._display_format_type == self.DisplayFormat.TIFRMVersion:
            new_value = (new_value & ((1 << 32) - 1)) \
                if new_value is not None else ''
            version = parse_value_for_display(
                value=new_value, precision=self.precision,
                display_format_type=self.DisplayFormat.Hex,
                string_encoding=self._string_encoding, widget=self)
            self.setText(version)
            return

        new_value = parse_value_for_display(
            value=new_value, precision=self.precision,
            display_format_type=self._display_format_type,
            string_encoding=self._string_encoding, widget=self)
        # If the value is a string, just display it as-is, no formatting
        # needed.
        if isinstance(new_value, str):
            if self._show_units and self._unit != "":
                new_value = "{} {}".format(new_value, self._unit)
            self.setText(new_value)
            return
        # If the value is an enum, display the appropriate enum string for
        # the value.
        if self.enum_strings and isinstance(new_value, (int, float)):
            try:
                self.setText(self.enum_strings[int(new_value)])
            except IndexError:
                self.setText(f'Index Overflow [{new_value}]')
            return
        # If the value is a number (float or int), display it using a
        # format string if necessary.
        if isinstance(new_value, (int, float)):
            if self._show_units and self._unit != '' and not self._keep_unit:
                new_value *= self._conv
                sc, prf = func.siScale(new_value)
                self.setText(self.format_string.format(sc*new_value, prf))
            else:
                self.setText(self.format_string.format(new_value))
            return
        # If you made it this far, just turn whatever the heck the value
        # is into a string and display it.
        self.setText(str(new_value))


class CALabel(QLabel, PyDMPrimitiveWidget):
    """QLabel with rules."""
