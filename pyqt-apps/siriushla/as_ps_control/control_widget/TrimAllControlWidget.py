"""Widgets to control Trim Quadrupoles magnets."""
from .BasePSControlWidget import BasePSControlWidget


class SITrimAllControlWidget(BasePSControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def __init__(self, **kwargs):
        """Get trim name."""
        super().__init__(**kwargs)

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "Q(D|F|[1-4]).*"}

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Focusing Quadrupoles Trims', "-QF"),
                ('Defocusing Quadrupoles Trims', "-QD"),
                ('Dispersive Quadrupoles Trims', "-Q[1-4]")]
