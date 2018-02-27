"""Define control widget for family sextupoles."""

from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class SIFamSextupoleControlWidget(BasePSControlWidget):
    """Storage ring sextupoles."""

    def _getPattern(self):
        return "SI-Fam:PS-S(\w+[0-9]*|[0-9])"

    def _getFilter(self):
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

    def _getPattern(self):
        return "BO-Fam:PS-S(\w+[0-9]*|[0-9])"

    def _getFilter(self):
        return {"sec": "BO", "sub": "Fam", "dev": "S[DF].*"}

    def _hasScrollArea(self):
        return False


def run_test(psname_list=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla import util

    app = SiriusApplication()
    util.set_style(app)
    window = SIFamSextupoleControlWidget(psname_list=psname_list)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
