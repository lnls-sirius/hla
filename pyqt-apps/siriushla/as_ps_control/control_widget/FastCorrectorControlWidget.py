"""Define control widget for fast correctors."""
from .BasePSControlWidget import BasePSControlWidget


class SIFastCorrectorControlWidget(BasePSControlWidget):
    """Storage ring fast correctors."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "SI", "sub": "\w{4}", "dev": "(FCH|FCV).*"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Horizontal Fast Correctors', '-FCH'),
                ('Vertical Fast Corretors', '-FCV')]

    def _getVisibleProps(self):
        return ['detail', 'state', 'alarm', 'setpoint', 'monitor',
                'strength_sp', 'strength_mon']
