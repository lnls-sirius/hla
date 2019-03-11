"""Main window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTabWidget

from siriushla.widgets import SiriusMainWindow
from siriushla.as_ap_energybutton.energy_setter import EnergySetter
from siriushla.as_ap_energybutton.energy_button import EnergyButton


class EnergySetterWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None):
        """."""
        super().__init__(parent)
        self._widgets = list()
        self._setup_ui()
        self.setWindowTitle('Energy Button Application')
        self.setFocusPolicy(Qt.StrongFocus)
        # self._connect_signal_and_slots()

    def _setup_ui(self):
        self._central_widget = QTabWidget(self)
        # self._central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(self._central_widget)

        self._create_widgets()

        for widget in self._widgets:
            self.centralWidget().addTab(widget, widget.setter.section.upper())

    def _create_widgets(self):
        for section in ('tb', 'bo'):
            self._widgets.append(EnergyButton(EnergySetter(section)))


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = EnergySetterWindow()
    w.show()
    sys.exit(app.exec_())
