"""Interface to set dipole energies with constant normalization."""

from qtpy.QtWidgets import QVBoxLayout, QWidget, QDoubleSpinBox, QPushButton, \
    QListWidget
from pydm.widgets import PyDMLabel

from siriuspy.envars import vaca_prefix as _vaca_prefix


class EnergyButton(QWidget):
    """Set dipole energy."""

    def __init__(self, setter, parent=None):
        """Setups widget interface."""
        super().__init__(parent)
        self.setter = setter
        self._setup_ui()

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())

        self.energy_value = QDoubleSpinBox(self)
        self.energy_value.setSingleStep(0.01)
        self.energy_value.setMinimum(self.setter.lower_limit)
        self.energy_value.setMaximum(self.setter.upper_limit)
        self.energy_value.setDecimals(4)

        if self.setter.section == 'tb':
            sp_channel = _vaca_prefix + 'TB-Fam:MA-B:Energy-RB'
        elif self.setter.section == 'bo':
            sp_channel = _vaca_prefix + 'BO-Fam:MA-B:Energy-RB'
        else:
            raise RuntimeError
        self.energy_sp = PyDMLabel(self)
        self.energy_sp.channel = sp_channel
        self.energy_sp.showUnits = True

        self.set_energy = QPushButton('Set', self)
        self.set_energy.clicked.connect(self._process)

        self.failed = QListWidget(self)

        # self.layout().addWidget(self.section)
        self.layout().addWidget(self.energy_value)
        self.layout().addWidget(self.energy_sp)
        self.layout().addWidget(self.set_energy)
        self.layout().addWidget(self.failed)

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
