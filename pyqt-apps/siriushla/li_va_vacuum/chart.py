from qtpy.QtWidgets import QVBoxLayout, QWidget
from siriushla.li_va_vacuum.functions import buildVacPv
from siriushla.widgets.timeplot import SiriusTimePlot
from .util import COLORS, PVS_CONFIG
from ..widgets import SiriusMainWindow

class ChartWindow(SiriusMainWindow):
    """Show the Chart Window."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self.config = PVS_CONFIG["Vacuum"]
        self.prefix = prefix
        self.main_dev = self.config["prefix"]
        self.devpref = self.prefix + self.main_dev
        self.channel = self.config['text']
        self.defaultColors = [
            COLORS["dark_green"], COLORS["red"], COLORS["blue"]]
        self.setObjectName('LIApp')
        self.setWindowTitle("CCG Charts")
        self._setupUi()

    def showGraph(self):
        graph = SiriusTimePlot(parent=self, background='w')
        graph.showLegend = False
        graph.showXGrid = True
        graph.showYGrid = True
        graph.autoRangeY = True
        graph.timeSpan = 10*60
        graph.bufferSize = graph.timeSpan*10

        graph.setStyleSheet("min-width: 15em; min-height: 10em;")
        return graph

    def addChannels(self, graph, id_num, color):
        name, gen = buildVacPv(self.config, id_num)
        pv_name = name+self.channel+str(gen)
        graph.addYChannel(
            y_channel=pv_name, axis='left', name='Vacuum',
            color=color, lineWidth=1)
        return graph

    def chartsMon(self, lay):
        id_num = 1
        for num in range(0, 3):
            graph = self.showGraph()
            for id_temp in range(0, 3):
                if id_num%3 == 0:
                    id_num += 1
                graph = self.addChannels(
                    graph, id_num, self.defaultColors[id_temp])
                id_num += 1
            lay.addWidget(graph)
        
    def _setupUi(self):
        """Display the selected chart type."""
        lay = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(lay)
        self.setCentralWidget(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        self.chartsMon(lay)
