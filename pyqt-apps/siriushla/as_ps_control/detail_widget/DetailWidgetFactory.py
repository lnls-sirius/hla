"""This module defines a factory to get a detailed window."""
import re

from siriushla.as_ps_control.detail_widget.PSDetailWidget \
    import PSDetailWidget
from siriushla.as_ps_control.detail_widget.DipoleDetailWidget \
    import DipoleDetailWidget
from siriushla.as_pm_control.PulsedMagnetDetailWidget \
    import PulsedMagnetDetailWidget


class DetailWidgetFactory:
    """Return a detail widget."""

    FamDipole = re.compile("^(SI|BO)-Fam:MA-B.*$")
    PulsedMagnet = re.compile("^.*:PM.*$")

    @staticmethod
    def factory(psname, parent=None):
        """Return a DetailWindow."""
        if DetailWidgetFactory.PulsedMagnet.match(psname):
            return PulsedMagnetDetailWidget(psname, parent)
        elif DetailWidgetFactory.FamDipole.match(psname):
            return DipoleDetailWidget(psname, parent)
        else:
            return PSDetailWidget(psname, parent)
