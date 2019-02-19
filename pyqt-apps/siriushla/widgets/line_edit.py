"""PyDMLine edit with validator."""
import locale

from qtpy.QtCore import QRegExp
from qtpy.QtGui import QRegExpValidator

from pydm.widgets.line_edit import PyDMLineEdit


class SiriusLineEdit(PyDMLineEdit):
    """LineEdit with validator."""

    def update_format_string(self):
        """
        Accept a unit to display with a channel's value

        The unit may or may not be displayed based on the :attr:`showUnits`
        attribute. Receiving a new value for the unit causes the display to
        reset.
        """
        if self.channeltype is float:
            decimal_point = locale.localeconv()['decimal_point']
            # decimal_point = '.'
            if self._show_units and self._unit != "":
                re = QRegExp(
                    '(-?)(0|([1-9][0-9]*))(\\{}[0-9]+)?( {})?'
                    .format(decimal_point, self._unit))
            else:
                re = QRegExp('(-?)(0|([1-9][0-9]*))(\\{}[0-9]+)?'
                             .format(decimal_point))
            validator = QRegExpValidator(re, self)
            self.setValidator(validator)
        super().update_format_string()
