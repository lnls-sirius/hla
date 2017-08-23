"""Widgets to control Fam Quadrupoles magnets."""

from pydm.PyQt.QtGui import QPushButton, QSizePolicy
from .BaseMagnetControlWidget import BaseMagnetControlWidget


class SiFamQuadrupoleControlWidget(BaseMagnetControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def _getPattern(self):
        return "SI-Fam:MA-Q(\w+[0-9]*|[0-9])"

    def _getStrength(self):
        return "KL"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon",
                "KL-SP", "KL-Mon", "Trim"]

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', "-QD"),
                ('Dispersive Quadrupoles', "-Q[0-9]")]

    # def _createGroupWidgets(self, ma):
    #     # magnet_widgets = super()._createGroupWidgets(ma)
    #     magnet_widget = super()._createGroupWidgets(ma)
    #
    #     # if self._hasTrimButton():
    #     #     trim_btn = QPushButton(">", self)
    #     #     trim_btn.setObjectName("trim_" + ma)
    #     #     magnet_widget.layout.addWidget(trim_btn)
    #
    #     return magnet_widget


class BoFamQuadrupoleControlWidget(SiFamQuadrupoleControlWidget):
    """Class to control a Fam Quad from the Booster section."""

    def _getPattern(self):
        return "BO-Fam:MA-Q(\w+[0-9]*|[0-9])"

    def _getHeader(self):
        return ["State", "Magnet", "Cur-SP", "Cur-Mon",
                "KL-SP", "KL-Mon"]

    def _hasTrimButton(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', "-QD")]
