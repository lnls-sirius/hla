"""Define widget for controlling slow correctors."""
from .BasePSControlWidget import BasePSControlWidget


class LILensControlWidget(BasePSControlWidget):
    """Linac Lens control widget."""

    def _getFilter(self, subsection=None):
        return {"sec": "LI", "dev": "Lens.*"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Lens', '-Lens-'),
                ('Lens Rev', '-LensRev')]


class ITLensControlWidget(BasePSControlWidget):
    """Injector Test Lens control widget."""

    def _getFilter(self, subsection=None):
        return {"sec": "IT", "dev": "Lens"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Lens', '-Lens-'), ]
