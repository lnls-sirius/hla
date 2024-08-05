"""Scale widgets."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QSizePolicy as QSzPlcy
from pydm.widgets.scale import QScale, PyDMScaleIndicator

class BaseScale(QScale):
    """QScale rederivation."""

    def calculate_position_for_value(self, value):
        """Rederivate calculate_position_for_value."""
        if value is None or value < self._lower_limit:
            proportion = -1  # Invalid
        elif value > self._upper_limit or\
                self._upper_limit - self._lower_limit == 0:
            proportion = 1  # Full
        else:
            proportion = (value - self._lower_limit) / \
                (self._upper_limit - self._lower_limit)

        position = int(proportion * self._widget_width)
        return position


class SiriusScaleIndicator(PyDMScaleIndicator):
    """PyDMScaleIndicator rederivation."""

    def __init__(self, parent=None, init_channel=None):
        """."""
        super().__init__(parent, init_channel=init_channel)
        self._show_value = True
        self._show_limits = True

        self.scale_indicator = BaseScale()
        self.value_label = QLabel()
        self.lower_label = QLabel()
        self.upper_label = QLabel()

        self.value_label.setText('<val>')
        self.lower_label.setText('<min>')
        self.upper_label.setText('<max>')

        self._value_position = Qt.TopEdge
        self._limits_from_channel = True
        self._user_lower_limit = 0
        self._user_upper_limit = 0

        self.value_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Minimum)
        self.setup_widgets_for_orientation(
            Qt.Horizontal, False, False, self._value_position)
