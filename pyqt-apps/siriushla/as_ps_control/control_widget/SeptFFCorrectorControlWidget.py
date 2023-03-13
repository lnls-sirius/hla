"""Define control widget for fast correctors."""
from .BasePSControlWidget import BasePSControlWidget


class SISeptFFCorrectorControlWidget(BasePSControlWidget):
    """Storage ring fast correctors."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "SI", "sub": "01M.*", "dev": "(FFCH|FFCV).*"}
        return filt

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Horizontal Septa FF Correctors', '-FFCH'),
                ('Vertical Septa FF Corretors', '-FFCV')]
