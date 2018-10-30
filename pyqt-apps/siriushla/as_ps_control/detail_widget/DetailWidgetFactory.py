"""This module defines a factory to get a detailed window."""
import re

from siriuspy.pwrsupply.data import PSData
from siriushla.as_ps_control.detail_widget.PSDetailWidget \
    import PSDetailWidget, FBPDCLinkDetailWidget, FACDCLinkDetailWidget
from siriushla.as_ps_control.detail_widget.DipoleDetailWidget \
    import DipoleDetailWidget
from siriushla.as_pm_control.PulsedMagnetDetailWidget \
    import PulsedMagnetDetailWidget
from qtpy.QtWidgets import QWidget, QGridLayout


class DetailWidgetFactory:
    """Return a detail widget."""

    FamDipole = re.compile("^(SI|BO)-Fam:MA-B.*$")
    PulsedMagnet = re.compile("^.*:PM.*$")

    @staticmethod
    def factory(psname, parent=None):
        """Return a DetailWidget."""
        if isinstance(psname, (list, tuple)):
            if len(psname) > 1:
                widget = QWidget(parent)
                widget.layout = QGridLayout(widget)
                n_lines = int(len(psname)/4)
                for idx, name in enumerate(psname):
                    widget.layout.addWidget(
                        DetailWidgetFactory._item(name, widget),
                        idx % n_lines,
                        int(idx / n_lines))
                return widget
            else:
                psname = psname[0]
        return DetailWidgetFactory._item(psname, parent)

    @staticmethod
    def _item(psname, parent=None):
        if DetailWidgetFactory.PulsedMagnet.match(psname):
            return PulsedMagnetDetailWidget(psname, parent)
        elif DetailWidgetFactory.FamDipole.match(psname):
            return DipoleDetailWidget(psname, parent)
        elif 'DCLink' in psname:
            model = PSData(psname).psmodel
            if model == 'FBP_DCLink':
                return FBPDClinkDetailWidget(psname, parent)
            elif model in ('FAC_ACDC', 'FAC_2P4S_ACDC'):
                return FACDCLinkDetailWidget(psname, parent)
            else:
                raise ValueError('Undefined PS model: {}'.format(model))
        else:
            return PSDetailWidget(psname, parent)
