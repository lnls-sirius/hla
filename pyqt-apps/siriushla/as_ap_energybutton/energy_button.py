"""Interface to set dipole energies with constant normalization."""

from qtpy.QtWidgets import QVBoxLayout, QWidget, QDoubleSpinBox, QPushButton, \
    QListWidget
from pydm.widgets import PyDMLabel


class EnergyButton(QWidget):
    """Set dipole energy."""

    def __init__(self, setter, parent=None):
        """Setups widget interface."""
        super().__init__(parent)
        self.setter = setter
        self._setup_ui()
        self._connect_signal_and_slots()

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())

        # self.section = QLabel("<h3>" + self.setter.section.upper() + "</h3>")
        self.energy_value = QDoubleSpinBox(self)
        if self.setter.section == 'tb':
            self.energy_sp = PyDMLabel(self, 'TB-Fam:MA-B:Energy-SP')
        elif self.setter.section == 'bo':
            self.energy_sp = PyDMLabel(self, 'BO-Fam:MA-B:Energy-SP')
        else:
            raise RuntimeError
        self.set_energy = QPushButton('Set', self)
        self.failed = QListWidget(self)

        # self.layout().addWidget(self.section)
        self.layout().addWidget(self.energy_value)
        self.layout().addWidget(self.energy_sp)
        self.layout().addWidget(self.set_energy)
        self.layout().addWidget(self.failed)

        self.energy_value.setSingleStep(0.01)
        self.energy_value.setMinimum(self.setter.lower_limit)
        self.energy_value.setMaximum(self.setter.upper_limit)
        self.energy_value.setDecimals(4)

        self.energy_sp.showUnits = True

    def _connect_signal_and_slots(self):
        self.set_energy.clicked.connect(self._process)

    def _process(self):
        failed = self.setter.set_values(self.energy_value.value())
        self.failed.clear()
        if not failed:
            self.failed.addItems(['No errors'])
        else:
            self.failed.addItems(failed)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla.as_ap_energybutton.energy_setter import EnergySetter

    app = SiriusApplication()
    setter = EnergySetter('tb')
    w = EnergyButton(setter)
    w.show()
    sys.exit(app.exec_())
