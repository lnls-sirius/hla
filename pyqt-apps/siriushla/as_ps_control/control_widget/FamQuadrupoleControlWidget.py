"""Widgets to control Fam Quadrupoles magnets."""

from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class SIFamQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def _getPattern(self):
        return "SI-Fam:PS-Q(\w+[0-9]*|[0-9])"

    def _getFilter(self):
        return {"sec": "SI", "sub": "Fam", "dev": "Q[DF0-9].*"}

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
        return False

    def _divideBySection(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', "-QD"),
                ('Dispersive Quadrupoles', "-Q[0-9]")]

    # def _createGroupWidgets(self, ma):
    #     # magnet_widgets = super()._createGroupWidgets(ma)
    #     magnet_widget = super()._createGroupWidgets(ma)
    #
    #     # if self._hasTrimButton():
    #     #     trim_btn = QPushButton(">", self)
    #     #     trim_btn.setObjectName("trim_" + ma)
    #     #     magnet_widget.layout.addWidget(trim_btn)
    #
    #     return magnet_widget


class BOFamQuadrupoleControlWidget(SIFamQuadrupoleControlWidget):
    """Class to control a Fam Quad from the Booster section."""

    def _getPattern(self):
        return "BO-Fam:PS-Q(\w+[0-9]*|[0-9])"

    def _getFilter(self):
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
    from siriushla import util

    app = SiriusApplication()
    util.set_style(app)
    window = SIFamQuadrupoleControlWidget(psname_list=psname_list)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
