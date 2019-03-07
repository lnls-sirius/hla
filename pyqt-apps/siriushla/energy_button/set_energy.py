"""set energy module."""

class EnergySetter:

    def __init__(self, section):
        self._section = section
        self._dipoles, self._magnets = init_section(section)

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
        print('setting magnet currents using energy: ', energy)
        set_energy(energy, self._dipoles, self._magnets)


def init_section(section):
    return None, None


def set_energy(energy, dipole, magnets):
    print(energy, dipole, magnets)
    return []


if __name__ == '__main__':
    e = EnergySetter('tb')