"""Interface to set dipole energies with constant normalization."""

from qtpy.QtWidgets import QVBoxLayout, QWidget, QDoubleSpinBox, QPushButton, \
    QLabel


class EnergyButton(QWidget):
    """Set dipole energy."""

    def __init__(self, setter, parent=None):
        """Setups widget interface."""
        super().__init__(parent)
        self._setter = setter
        self._setup_ui()
        self._connect_signal_and_slots()

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())

        self.section = QLabel("<h3>" + self._setter.section.upper() + "</h3>")
        self.energy_value = QDoubleSpinBox(self)
        self.set_energy = QPushButton('Set', self)

        self.layout().addWidget(self.section)
        self.layout().addWidget(self.energy_value)
        self.layout().addWidget(self.set_energy)

        self.energy_value.setSingleStep(0.1)
        self.energy_value.setMinimum(self._setter.lower_limit)
        self.energy_value.setMaximum(self._setter.upper_limit)

    def _connect_signal_and_slots(self):
        self.set_energy.clicked.connect(
            lambda: self._setter.set_values(self.energy_value.value()))


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla.energy_button.set_energy import EnergySetter

    app = SiriusApplication()
    setter = EnergySetter('tb')
    w = EnergyButton(setter)
    w.show()
    sys.exit(app.exec_())
