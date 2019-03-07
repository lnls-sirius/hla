"""set energy module."""

from qtpy.QtCore import Signal, QThread
from siriushla.energy_button.set_energy import init_section, set_energy


class EnergySetter:

    itemDone = Signal(str)
    itemFailed = Signal(str)

    def __init__(self, section):
        self._section = section
        self._dipoles, self._magnets = init_section(section.upper())

    @property
    def section(self):
        return self._section

    @property
    def upper_limit(self):
        if self.section == 'tb':
            return 300.0
        elif self.section == 'bo':
            return 60.0
        else:
            raise RuntimeError

    @property
    def lower_limit(self):
        if self.section == 'tb':
            return 0.0
        elif self.section == 'bo':
            return -60.0
        else:
            raise RuntimeError

    def set_values(self, energy):
        print('setting magnet currents using energy: ', self.section, energy)
        return set_energy(energy, self._dipoles, self._magnets)
