"""This module defines a factory to get a detailed window."""
from qtpy.QtWidgets import QWidget, QGridLayout, QScrollArea
from siriuspy.search import PSSearch
from .PSDetailWidget import PSDetailWidget, FBPDCLinkDetailWidget, \
    FACDCLinkDetailWidget, LIPSDetailWidget, FastCorrPSDetailWidget


class DetailWidgetFactory:
    """Return a detail widget."""

    @staticmethod
    def factory(psname, parent=None, psmodel=None, pstype=None):
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
        return DetailWidgetFactory._item(
            psname, parent=parent, psmodel=psmodel, pstype=pstype)

    @staticmethod
    def _item(psname, parent=None, psmodel=None, pstype=None):
        if not psmodel:
            try:
                psmodel = PSSearch.conv_psname_2_psmodel(psname)
            except (ValueError, KeyError):
                if psname.startswith('LI'):
                    psmodel = 'LINAC_PS'
                elif '-FC' in psname:
                    psmodel = 'FOFB_PS'
                else:
                    raise ValueError(f'Undefined PS model for psname {psname}')
        if psmodel == 'FBP_DCLink':
            return FBPDCLinkDetailWidget(psname, parent)
        if psmodel in ('FAC_2S_ACDC', 'FAC_2P4S_ACDC'):
            return FACDCLinkDetailWidget(psname, parent)
        if psmodel == 'LINAC_PS':
            return LIPSDetailWidget(psname, parent)
        if psmodel == 'FOFB_PS':
            return FastCorrPSDetailWidget(psname, parent)
        return PSDetailWidget(
            psname, parent=parent, psmodel=psmodel, pstype=pstype)
