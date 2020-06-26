"""Axiliary Dialogs Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel
from qtpy.QtGui import QColor
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.widgets import SiriusDialog
from .custom_widgets import WfmGraph


class CoeffFFTView(SiriusDialog):
    """Coefficients FFT View."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.dev_pref = prefix + device
        self.setWindowTitle(self.device+' Coefficients FFT')
        self.setObjectName('SIApp')
        self._setupUi()

    def _setupUi(self):
        self._lb_fftmag = QLabel(
            '<h4>Magnitude</h4>', self, alignment=Qt.AlignCenter)
        self._graph_fftmag = WfmGraph(self)
        self._graph_fftmag.addChannel(
            y_channel=self.dev_pref+':FTF_MAG', color=QColor('blue'),
            lineWidth=2, lineStyle=Qt.SolidLine)

        self._lb_fftphs = QLabel(
            '<h4>Phase</h4>', self, alignment=Qt.AlignCenter)
        self._graph_fftphs = WfmGraph(self)
        self._graph_fftphs.addChannel(
            y_channel=self.dev_pref+':FTF_PHASE', color=QColor('red'),
            lineWidth=2, lineStyle=Qt.SolidLine)

        lay = QGridLayout(self)
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel('<h3>Coefficients FFT</h3>',
                             self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(self._lb_fftmag, 1, 0)
        lay.addWidget(self._graph_fftmag, 2, 0)
        lay.addWidget(self._lb_fftphs, 3, 0)
        lay.addWidget(self._graph_fftphs, 4, 0)
