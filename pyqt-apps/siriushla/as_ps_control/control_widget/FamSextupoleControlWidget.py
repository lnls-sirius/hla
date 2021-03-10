"""Define control widget for family sextupoles."""

from .BasePSControlWidget import BasePSControlWidget


class SIFamSextupoleControlWidget(BasePSControlWidget):
    """Storage ring sextupoles."""

    def _getFilter(self, subsection=None):
        return {"sec": "SI", "sub": "Fam", "dev": "S[DF].*"}

    def _getStrength(self):
        return "SL"

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Focusing Sextupoles', '-SF'),
                ('Defocusing Sextupoles', '-SD')]


class BOFamSextupoleControlWidget(SIFamSextupoleControlWidget):
    """Booster sextupoles."""

    def _getFilter(self, subsection=None):
        return {"sec": "BO", "sub": "Fam", "dev": "S[DF].*"}

    def _hasScrollArea(self):
        return False


def run_test(psname_list=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    window = SIFamSextupoleControlWidget(psname_list=psname_list)
    window.show()
    sys.exit(app.exec_())
