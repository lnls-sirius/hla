"""BbB Devices Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QTabWidget, \
    QGroupBox, QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy, \
    QVBoxLayout, QSpacerItem

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.widgets import PyDMStateButton, PyDMLed, SiriusFrame
from .custom_widgets import WfmGraph, MyScaleIndicator


class BbBMasksWidget(QWidget):
    """BbB Masks Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_exct_masks = QLabel(
            '<h3>Excitation Masks</h3>', self,
            alignment=Qt.AlignCenter)
        self._ld_spec_masks = QLabel(
            '<h3>Spectrum Averaging Masks</h3>', self,
            alignment=Qt.AlignCenter)

        self._graph_exct = WfmGraph(self)
        self._graph_exct.showLegend = True
        self._graph_exct.axisColor = QColor('black')
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':FB_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Feedback', color=QColor('blue'))
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':CF_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Alternate', color=QColor('green'))
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':DRIVE_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Drive', color=QColor('red'))

        self._graph_spec = WfmGraph(self)
        self._graph_spec.showLegend = True
        self._graph_spec.axisColor = QColor('black')
        self._graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':SRAM_ACQ_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='SRAM', color=QColor('red'))
        self._graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':BRAM_ACQ_MASK',
            xchannel=self.dev_pref+':BRAM_XSC',
            name='BRAM', color=QColor('blue'))

        lay = QGridLayout(self)
        lay.addWidget(self._ld_exct_masks, 0, 0)
        lay.addWidget(self._graph_exct, 1, 0)
        lay.addItem(QSpacerItem(20, 20), 2, 0)
        lay.addWidget(self._ld_spec_masks, 3, 0)
        lay.addWidget(self._graph_spec, 4, 0)
