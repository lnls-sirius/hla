"""Main window."""

from qtpy.QtWidgets import QVBoxLayout, QWidget

from siriushla.widgets import SiriusMainWindow
from siriushla.energy_button.set_energy import EnergySetter
from siriushla.energy_button.energy_button import EnergyButton


class EnergySetterWindow(SiriusMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self._central_widget = QWidget(self)
        self._central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(self._central_widget)

        for widget in self._create_widgets():
            self.centralWidget().layout().addWidget(widget)

    def _create_widgets(self):
        widgets = list()
        for section in ('tb', 'bo'):
            widgets.append(EnergyButton(EnergySetter(section)))
        return widgets


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    
    app = SiriusApplication()
    w = EnergySetterWindow()
    w.show()
    sys.exit(app.exec_())