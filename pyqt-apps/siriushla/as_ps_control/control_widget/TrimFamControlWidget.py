"""Widgets to control Trim Quadrupoles magnets."""
from .BasePSControlWidget import BasePSControlWidget


class SITrimFamControlWidget(BasePSControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def __init__(self, trim, **kwargs):
        """Get trim name."""
        self._trim = trim
        super().__init__(**kwargs)

    def _getFilter(self, subsection=None):
        return {"sec": "SI", "sub": "\w{4}", "dev": self._trim}

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Trims', "")]
