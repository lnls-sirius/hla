"""Define widget for controlling idff correctors."""
from .BasePSControlWidget import BasePSControlWidget


class IDFFCorrectorControlWidget(BasePSControlWidget):
    """IDFF corrector control widget."""

    def _getFilter(self, subsection=None):
        subsectype = subsection[-1]  # 'A' | 'B' | 'P'
        qd = "QD" + subsectype  # for A type sections
        qf = "QF" + subsectype
        qd1 = qd + "1"  # for B and P type sections
        qd2 = qd + "2"  # for B and P type sections
        trims = qd + "|" + qd1 + "|" + qf + "|" + qd2
        dev = "(CH|CV|QS|" + trims + "|LCH|CC1|CC2)"
        return {"sec": "SI", "sub": subsection, "dev": dev}

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [
            ('Horizontal Correctors', '-CH'),
            ('Vertical Corretors', '-CV'),
            ('Skew Quadrupole', '-QS'),
            ('Trim Quadrupoles ', '-(QF[ABP]|QDA|QDB[12]|QDP[12])'),
            ('Long Coils', '-LCH'),
            ('Corrector Coils', '-CC')
            ]
