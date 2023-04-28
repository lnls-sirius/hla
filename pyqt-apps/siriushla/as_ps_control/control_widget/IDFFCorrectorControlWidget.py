"""Define widget for controlling idff correctors."""
from .BasePSControlWidget import BasePSControlWidget


class IDFFCorrectorControlWidget(BasePSControlWidget):
    """IDFF corrector control widget."""

    def _getFilter(self, subsection=None):
        return {"sec": "SI", "sub": subsection, "dev": "(CH|CV|QS)"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Horizontal Correctors', '-CH'),
                ('Vertical Corretors', '-CV'),
                ('Skew Quadrupole', '-QS')]
