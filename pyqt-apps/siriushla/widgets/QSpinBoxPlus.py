"""Module to define QSpinBoxPlus and QDoubleSpinBoxPlus."""

from qtpy.QtWidgets import QSpinBox, QDoubleSpinBox, QApplication
from qtpy.QtCore import Qt, QLocale


def _create_spinboxplus(qt_type):
    """Create SpinBoxPlus."""

    class MySpinBoxPlus(qt_type):
        """Subclass to reimplement wheelEvent and keyPressEvent."""

        def __init__(self, *args, **kwargs):
            """Initialize object."""
            super().__init__(*args, **kwargs)
            locale = QLocale(QLocale.English, country=QLocale.UnitedStates)
            locale.setNumberOptions(locale.RejectGroupSeparator)
            self.setLocale(locale)
            self.setFocusPolicy(Qt.StrongFocus)
            self.step_exponent = 0
            self.app = QApplication.instance()

        def wheelEvent(self, evt):
            """Reimplement wheel event to ignore event when out of focus."""
            if not self.hasFocus():
                evt.ignore()
            else:
                super().wheelEvent(evt)

        def keyPressEvent(self, evt):
            ctrl_hold = self.app.queryKeyboardModifiers() == Qt.ControlModifier
            if ctrl_hold and (evt.key() in (Qt.Key_Left, Qt.Key_Right)):
                self.step_exponent += 1 if evt.key() == Qt.Key_Left else -1
                if isinstance(self, QSpinBox):
                    self.step_exponent = max(0, self.step_exponent)
                else:
                    self.step_exponent = max(-self.decimals(),
                                             self.step_exponent)
                self.setSingleStep(10 ** self.step_exponent)
            else:
                super().keyPressEvent(evt)

    return MySpinBoxPlus


QSpinBoxPlus = _create_spinboxplus(QSpinBox)
QDoubleSpinBoxPlus = _create_spinboxplus(QDoubleSpinBox)
