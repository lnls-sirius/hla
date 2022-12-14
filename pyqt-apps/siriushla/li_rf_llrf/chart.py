"""LI LLRF Chart Window."""

from qtpy.QtWidgets import QGridLayout, QWidget
from ..widgets import SiriusMainWindow
from .widgets import GraphTime, GraphIvsQ, GraphWave


class ChartWindow(SiriusMainWindow):
    """Show the Chart Window."""

    def __init__(self, parent=None, dev='', channel='', chart_type="Forward", prefix=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.main_dev = 'LA-RF:LLRF:'
        self.device = dev
        self.devpref = self.prefix + self.main_dev
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
            self, self.device, 'Time', self.devpref,
            self.channel, prefix=self.prefix)
        ivsq = GraphIvsQ(
            self, self.device, 'IvsQ', self.devpref,
            self.channel, prefix=self.prefix)
        amp = GraphTime(
            self, self.device, 'Amp', self.devpref,
            self.channel, prefix=self.prefix)
        pha = GraphTime(
            self, self.device, 'Pha', self.devpref,
            self.channel, prefix=self.prefix)
        lay.addWidget(iqtime, 0, 0)
        lay.addWidget(ivsq, 1, 0)
        lay.addWidget(amp, 0, 1)
        lay.addWidget(pha, 1, 1)

    def chartsPulseAmpPha(self, lay):
        """Show the pulse charts of Amplitude and Phase"""
        amp = GraphWave(
            self, self.device, 'PAmp', self.devpref,
            self.channel, prefix=self.prefix)
        pha = GraphWave(
            self, self.device, 'PPha', self.devpref,
            self.channel, prefix=self.prefix)
        lay.addWidget(amp, 0, 2)
        lay.addWidget(pha, 1, 2)

    def _setupUi(self):
        """Display the selected chart type."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)

        if self.chart_type in ["Reference", "VM"]:
            self.chartsIQAmpPha(lay)
        elif self.chart_type in ["Pick-Up", "Forward"]:
            self.chartsIQAmpPha(lay)
            self.chartsPulseAmpPha(lay)
        elif self.chart_type == 'Diff':
            lay.addWidget(
                GraphTime(self, self.device, 'Diff', self.devpref, prefix=self.prefix))
        else:
            lay.addWidget(
                GraphWave(self, self.device, 'Raw', self.devpref, prefix=self.prefix))

class ChartMon(QWidget):
    """Show the Chart Window."""

    def __init__(self, parent=None, dev='', prefix=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.main_dev = 'LA-RF:LLRF:'
        self.device = dev
        self.devpref = self.prefix + self.main_dev
        self.channel = 'CH1'
        self.setObjectName('LIApp')
        self._setupUi()

    def chartsMon(self, lay):
        ivsq = GraphIvsQ(
            self, self.device, 'IvsQ', self.devpref, self.channel, prefix=self.prefix)
        amp = GraphTime(
            self, self.device, 'Amp', self.devpref, self.channel, prefix=self.prefix)
        pha = GraphTime(
            self, self.device, 'Pha', self.devpref, self.channel, prefix=self.prefix)
        lay.addWidget(ivsq, 0, 0)
        lay.addWidget(amp, 0, 2)
        lay.addWidget(pha, 0, 4)

    def _setupUi(self):
        """Display the selected chart type."""
        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
        self.chartsMon(lay)
