"""This module defines a factory to get a detailed window."""
from qtpy.QtWidgets import QWidget, QGridLayout
from siriuspy.search import PSSearch
from .PSDetailWidget import PSDetailWidget, FBPDCLinkDetailWidget, \
    FACDCLinkDetailWidget


class DetailWidgetFactory:
    """Return a detail widget."""

    @staticmethod
    def factory(psname, parent=None):
        """Return a DetailWidget."""
        if isinstance(psname, (list, tuple)):
            if len(psname) > 1:
                widget = QWidget(parent)
                widget.layout = QGridLayout(widget)
                n_lines = int(len(psname)/4) or 1
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
        if 'DCLink' in psname:
            model = PSSearch.conv_psname_2_psmodel(psname)
            if model == 'FBP_DCLink':
                return FBPDCLinkDetailWidget(psname, parent)
            elif model in ('FAC_ACDC', 'FAC_2S_ACDC', 'FAC_2P4S_ACDC'):
                return FACDCLinkDetailWidget(psname, parent)
            else:
                raise ValueError('Undefined PS model: {}'.format(model))
        else:
            return PSDetailWidget(psname, parent)
