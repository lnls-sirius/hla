"""LI LLRF Chart Window."""

from qtpy.QtWidgets import QGridLayout, QWidget

from ..widgets import SiriusMainWindow, PyDMStateButton, SiriusLedState, \
    SiriusSpinbox, SiriusLabel
from .widgets import GraphTime, GraphIvsQ


class ChartWindow(SiriusMainWindow):
    """Show the Chart Window."""

    def __init__(self, parent=None, dev='', channel='', chart_type="Forward"):
        """Init."""
        super().__init__(parent)
        self.prefix = 'LA-RF:LLRF:'
        self.device = dev
        self.channel = channel
        self.chart_type = chart_type

        self.setObjectName('LIApp')

        if channel != '':
            self.setWindowTitle(
                self.device + " " + self.channel +
                " " + chart_type + ' Chart')
        else:
            self.setWindowTitle(chart_type + ' Chart')

        self._setupUi()

    def chartsIQAmpPha(self, lay):
        """Show the 4 basic charts"""
        """These being: I&Q, based on time and IxQ, Amplitude and Phase"""
        iqtime = GraphIvsQ(
            self, self.device, 'Time', self.prefix, self.channel)
        ivsq = GraphIvsQ(
            self, self.device, 'IvsQ', self.prefix, self.channel)
        amp = GraphTime(
            self, self.device, 'Amp', self.prefix, self.channel)
        pha = GraphTime(
            self, self.device, 'Pha', self.prefix, self.channel)
        lay.addWidget(iqtime, 0, 0)
        lay.addWidget(ivsq, 1, 0)
        lay.addWidget(amp, 0, 1)
        lay.addWidget(pha, 1, 1)

    def chartsPulseAmpPha(self, lay):
        """Show the pulse charts of Amplitude and Phase"""
        amp = GraphTime(self, self.device, 'PAmp', self.prefix, self.channel)
        pha = GraphTime(self, self.device, 'PPha', self.prefix, self.channel)
        lay.addWidget(amp, 0, 2)
        lay.addWidget(pha, 1, 2)

    def _setupUi(self):
        """Display the selected chart type."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout()
        wid.setLayout(lay)

        if self.chart_type in ["Reference", "VM"]:
            self.chartsIQAmpPha(lay)
        elif self.chart_type in ["Pick-Up", "Forward"]:
            self.chartsIQAmpPha(lay)
            self.chartsPulseAmpPha(lay)
        elif self.chart_type == 'Diff':
            lay.addWidget(
                GraphTime(self, self.device, 'Diff', self.prefix))
        else:
            lay.addWidget(
                GraphTime(self, self.device, 'Raw', self.prefix))
