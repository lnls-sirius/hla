"""Widgets to control Dipoles."""

from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class TBDipoleControlWidget(BasePSControlWidget):
    """Class to control Dipole power supplies."""

    def _getFilter(self):
        return {"sec": "TB", "sub": "Fam", "dev": "B.*"}

    def _getGroups(self):
        return [('Dipoles', "-B.*")]


class BODipoleControlWidget(BasePSControlWidget):
    """Class to control Dipole power supplies."""

    def _getFilter(self):
        return {"sec": "BO", "sub": "Fam", "dev": "B.*"}

    def _getGroups(self):
        return [('Dipoles', "-B.*")]


class TSDipoleControlWidget(BasePSControlWidget):
    """Class to control Dipole power supplies."""

    def _getFilter(self):
        return {"sec": "TS", "sub": "Fam", "dev": "B.*"}

    def _getGroups(self):
        return [('Dipoles', "-B.*")]


class SIDipoleControlWidget(BasePSControlWidget):
    """Class to control Dipole power supplies."""

    def _getFilter(self):
        return {"sec": "SI", "sub": "Fam", "dev": "B.*"}

    def _getGroups(self):
        return [('Dipoles', "-B.*")]
