"""BbB Devices Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QSpacerItem

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from .custom_widgets import WfmGraph
from .util import set_bbb_color


class BbBMasksWidget(QWidget):
    """BbB Masks Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_exct_masks = QLabel(
            '<h3>Excitation Masks</h3>', self, alignment=Qt.AlignCenter)
        ld_spec_masks = QLabel(
            '<h3>Spectrum Averaging Masks</h3>', self,
            alignment=Qt.AlignCenter)

        graph_exct = WfmGraph(self)
        graph_exct.setAutoRangeY(False)
        graph_exct.setYRange(-0.01, 1.08)
        graph_exct.showLegend = True
        graph_exct.axisColor = QColor('black')
        graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':FB_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Feedback', color=QColor('blue'))
        graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':CF_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Alternate', color=QColor('green'), offset=0.02)
        graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':DRIVE0_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Drive0', color=QColor('red'), offset=0.04)
        graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':DRIVE1_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Drive1', color=QColor('magenta'), offset=0.06)
        graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':DRIVE2_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Drive2', color=QColor('orange'), offset=0.08)
        graph_exct.setLabel('left', '')

        graph_spec = WfmGraph(self)
        graph_spec.setAutoRangeY(False)
        graph_spec.setYRange(-0.01, 1.08)
        graph_spec.showLegend = True
        graph_spec.axisColor = QColor('black')
        graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':SRAM_ACQ_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='SRAM', color=QColor('red'))
        graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':BRAM_ACQ_MASK',
            xchannel=self.dev_pref+':BRAM_XSC',
            name='BRAM', color=QColor('blue'), offset=0.02)
        graph_spec.setLabel('left', '')

        lay = QGridLayout(self)
        lay.addWidget(ld_exct_masks, 0, 0)
        lay.addWidget(graph_exct, 1, 0)
        lay.addItem(QSpacerItem(20, 20), 2, 0)
        lay.addWidget(ld_spec_masks, 3, 0)
        lay.addWidget(graph_spec, 4, 0)
