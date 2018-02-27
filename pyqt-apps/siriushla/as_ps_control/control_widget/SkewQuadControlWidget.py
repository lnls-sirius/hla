"""Sked Quadrupole control widgets."""

from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class SISkewQuadControlWidget(BasePSControlWidget):
    """Storage ring skew quads."""

    def _getPattern(self):
        return "SI-\w{4}:PS-QS"

    def _getFilter(self):
        return {"sec": "SI", "sub": "\w{4}", "dev": "QS"}

    def _getStrength(self):
        return "KL"

    def _hasTrimButton(self):
        return False

    def _hasScrollArea(self):
        return True

    def _divideBySection(self):
        return True

    def _getGroups(self):
        return [('Skew Quad (01 - 10)', '(0\d|10)'),
                ('Skew Quad (11 - 20)', '(1[1-9]|20)')]


class BOSkewQuadControlWidget(SISkewQuadControlWidget):
    """Booster skew quads."""

    def _getPattern(self):
        return "BO-\w{3}:PS-QS"

    def _getFilter(self):
        return {"sec": "BO", "sub": "\w{3}", "dev": "QS"}

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Skew Quad', '')]


def run_test(psname_list=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla import util

    app = SiriusApplication()
    util.set_style(app)
    window = SISkewQuadControlWidget(psname_list=psname_list)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
