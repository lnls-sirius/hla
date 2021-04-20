"""This module defines a factory to get a detailed window."""
from qtpy.QtWidgets import QWidget, QGridLayout, QScrollArea
from siriuspy.search import PSSearch
from .PSDetailWidget import PSDetailWidget, FBPDCLinkDetailWidget, \
    FACDCLinkDetailWidget, LIPSDetailWidget


class DetailWidgetFactory:
    """Return a detail widget."""

    @staticmethod
    def factory(psname, parent=None):
        """Return a DetailWidget."""
        if isinstance(psname, (list, tuple)):
            if len(psname) > 1:
                scrwidget = QWidget(parent)
                scrwidget.layout = QGridLayout(scrwidget)
                scrwidget.setObjectName('scrwidget')
                scrwidget.setStyleSheet(
                    '#scrwidget{background-color: transparent;}')
                scroll = QScrollArea(parent)
                scroll.setWidget(scrwidget)
                scroll.setWidgetResizable(True)
                scroll.setSizeAdjustPolicy(
                    QScrollArea.AdjustToContentsOnFirstShow)
                n_lines = int(len(psname)/4) or 1
                for idx, name in enumerate(psname):
                    scrwidget.layout.addWidget(
                        DetailWidgetFactory._item(name, parent),
                        idx % n_lines,
                        int(idx / n_lines))
                widget = QWidget()
                lay = QGridLayout(widget)
                lay.addWidget(scroll)
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
        elif 'LI' in psname:
            return LIPSDetailWidget(psname, parent)
        else:
            return PSDetailWidget(psname, parent)
