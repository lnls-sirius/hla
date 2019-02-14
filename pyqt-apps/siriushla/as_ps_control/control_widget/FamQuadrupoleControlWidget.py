"""Widgets to control Fam Quadrupoles magnets."""

from siriushla.as_ps_control.control_widget.BasePSControlWidget import \
    BasePSControlWidget


class TBQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control a quads from the TB transport line."""

    def _getFilter(self):
        return {"sec": "TB", "dev": "Q.*"}

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', '-QD')]


class TSQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control a quads from the TB transport line."""

    def _getFilter(self):
        return {"sec": "TS", "dev": "Q.*"}

    def _hasScrollArea(self):
        return False

    def _getGroups(self):
        return [('Focusing Quadrupoles', "-QF"),
                ('Defocusing Quadrupoles', '-QD')]


class SIFamQuadrupoleControlWidget(BasePSControlWidget):
    """Class to control a Fam Quad from the Sirius section."""

    def _getFilter(self):
        return {"sec": "SI", "sub": "Fam", "dev": "Q[DF0-9].*"}

    def _hasTrimButton(self):
        return True

    def _hasScrollArea(self):
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

    app = SiriusApplication()
    window = SIFamQuadrupoleControlWidget(dev_type=0)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
