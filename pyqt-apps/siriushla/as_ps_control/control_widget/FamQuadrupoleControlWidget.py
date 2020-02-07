"""Widgets to control Fam Quadrupoles magnets."""

from .BasePSControlWidget import BasePSControlWidget


class LIQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control all quads from the LI section."""

    def _getFilter(self, subsection=None):
        return {"sec": "LI", "dev": "Q.*"}

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', '-QD')]


class TBQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control all quads from the TB transport line."""

    def _getFilter(self, subsection=None):
        return {"sec": "TB", "dev": "Q.*"}

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', '-QD')]


class TSQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control all quads from the TB transport line."""

    def _getFilter(self, subsection=None):
        return {"sec": "TS", "dev": "Q.*"}

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', '-QD')]


class SIFamQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control all Fam Quad from the Sirius section."""

    def _getFilter(self, subsection=None):
        return {"sec": "SI", "sub": "Fam", "dev": "Q[DF0-9].*"}

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Dispersive Quadrupoles', "-Q[1-4]"),
                ('Defocusing Quadrupoles', "-QD")]


class BOFamQuadrupoleControlWidget(SIFamQuadrupoleControlWidget):
    """Class to control all Fam Quad from the Booster section."""

    def _getFilter(self, subsection=None):
        return {"sec": "BO", "sub": "Fam", "dev": "Q[DF0-9].*"}

    def _hasTrimButton(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', "-QD")]


def run_test(psname_list=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    window = SIFamQuadrupoleControlWidget(dev_type='PS')
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
