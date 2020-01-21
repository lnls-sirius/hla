"""Sked Quadrupole control widgets."""

from .BasePSControlWidget import BasePSControlWidget


class SISkewQuadControlWidget(BasePSControlWidget):
    """Storage ring skew quads."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "SI", "sub": "\w{4}", "dev": "QS"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _getStrength(self):
        return "KL"

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _getGroups(self):
        return [('Skew Quad', '')]


class BOSkewQuadControlWidget(SISkewQuadControlWidget):
    """Booster skew quads."""

    def _getFilter(self, subsection=None):
        filt = {"sec": "BO", "sub": "\w{3}", "dev": "QS"}
        if subsection:
            filt.update({'sub': subsection})
        return filt

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Skew Quad', '')]


def run_test(psname_list=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    window = SISkewQuadControlWidget(psname_list=psname_list)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
