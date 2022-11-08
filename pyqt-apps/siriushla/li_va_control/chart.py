""" CCG Chart Window """

from ..widgets import SiriusMainWindow, SiriusTimePlot
from .functions import BaseFunctionsInterface
from .util import COLORS, PVS_CONFIG, VGC_DETAILS


class ChartWindow(SiriusMainWindow, BaseFunctionsInterface):
    """Show the Chart Window."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self.config = PVS_CONFIG["Vacuum"]
        self.prefix = prefix
        self.main_dev = self.config["prefix"]
        self.devpref = self.prefix + self.main_dev
        self.channel = VGC_DETAILS["Pressure<br/>Readback"]
        self.default_colors = [
            COLORS["dark_green"], COLORS["red"], COLORS["blue"],
            COLORS["purple"], COLORS["light_green"], COLORS["yellow"],
            COLORS["cyan"], COLORS["gre_blu"], COLORS["black"],
            COLORS["orange"]]
        self.setObjectName('LIApp')
        self.setWindowTitle("CCG Charts")
        self._setupUi()

    def setupGraph(self):
        """Create and configure Chart Widget"""
        graph = SiriusTimePlot(parent=self, background='w')
        graph.setYLabels(["Pressure"])
        graph.showLegend = True
        graph.showXGrid = True
        graph.showYGrid = True
        graph.autoRangeY = True
        graph.timeSpan = 10*60
        graph.bufferSize = graph.timeSpan*10
        graph.setStyleSheet("min-width: 15em; min-height: 10em;")
        return graph

    def addChannels(self, graph, id_num, color):
        """Add one channel(curve) to the chart"""
        name, gen = self.buildVacPv(id_num)
        pv_name = self.config['prefix']+name+self.channel+str(gen)
        graph.addYChannel(
            y_channel=pv_name, axis='left',
            name=self.getGroupTitle("Vacuum", id_num),
            color=color, lineWidth=2)
        return graph

    def chartsMon(self, lay):
        """Display the three charts with their channels"""
        id_num = 1
        for num in range(0, 3):
            graph = self.setupGraph()
            range_max = 3
            if num == 1:
                range_max = 4
            for id_temp in range(0, range_max):
                graph = self.addChannels(
                    graph, id_num, self.default_colors.pop())
                id_num += 1
                if id_num % 3 == 0:
                    id_num += 1
            lay.addWidget(graph)

    def _setupUi(self):
        """."""
        wid, lay = self.getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 10, 10, 10)
        self.chartsMon(lay)
