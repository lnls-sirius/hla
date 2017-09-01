"""This module defines a factory to get a detailed window."""
import re

from siriushla.as_ma_control.detail_widget.MagnetDetailWidget \
    import MagnetDetailWidget
from siriushla.as_ma_control.detail_widget.DipoleDetailWidget \
    import DipoleDetailWidget
from siriushla.as_pm_control.PulsedMagnetDetailWidget \
    import PulsedMagnetDetailWidget


class DetailWidgetFactory:
    """Return a detail widget."""

    FamDipole = re.compile("^(SI|BO)-Fam:MA-B.*$")
    PulsedMagnet = re.compile("^.*:PM.*$")

    @staticmethod
    def factory(maname, parent=None):
        """Return a DetailWindow."""
        if DetailWidgetFactory.PulsedMagnet.match(maname):
            return PulsedMagnetDetailWidget(maname, parent)
        elif DetailWidgetFactory.FamDipole.match(maname):
            return DipoleDetailWidget(maname, parent)
        else:
            return MagnetDetailWidget(maname, parent)
