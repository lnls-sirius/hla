"""Define control widget for fast correctors."""
from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class SIFastCorrectorControlWidget(BasePSControlWidget):
    """Storage ring fast correctors."""

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "(FCH|FCV).*"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Horizontal Fast Correctors', '-FCH'),
                ('Vertical Fast Corretors', '-FCV')]
