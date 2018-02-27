"""Widgets to control Trim Quadrupoles magnets."""
from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class TrimControlWidget(BaseMagnetControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def _getPattern(self):
        return "SI-\d{2}\w\d:PS-Q[DF0-9].*"

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "Q[DF0-9].*"}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Trims (1-10)', "SI-(0\d|10)"),
                ('Trims (11-20)', "SI-(1[1-9]|20)")]
