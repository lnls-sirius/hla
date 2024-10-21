"""Temperature Profile Monitor."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QTabWidget

from ...widgets import DetachableTabWidget, SiriusDialog
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS
from .bar_graph import BarGraph


class TempMonitor(SiriusDialog):
    """Temperature Profile Monitor."""

    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle('RF Temperature Monitor')
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(25)
        lay.setVerticalSpacing(15)

        self.title = QLabel(
            '<h3>RF Temperature Monitor</h3>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title, 0, 0)

        if len(self.chs['TempMon']) == 1:
            dettab = QTabWidget(self)
        else:
            dettab = DetachableTabWidget(self)
        dettab.setObjectName(self.section+'Tab')
        for dettabtitle, dtcontent in self.chs['TempMon'].items():
            if dettabtitle == 'Power (Water)':
                labels = list(dtcontent.keys())
                channels = [self.prefix+ch for ch in dtcontent.values()]
                wid = BarGraph(
                    channels=channels, xLabels=labels, yLabel='Power [kW]',
                    title=dettabtitle)
            else:
                wid = QTabWidget()
                for tabtitle, content in dtcontent.items():
                    labels = list(content.keys())
                    channels = [self.prefix+ch for ch in content.values()]
                    ylabel = 'Temperature [°C]' \
                        if 'temp' in dettabtitle.lower() \
                        else 'Diss. Power [kW]'
                    tabwid = BarGraph(
                        channels=channels, xLabels=labels,
                        yLabel=ylabel, title=dettabtitle)
                    wid.addTab(tabwid, tabtitle)
            dettab.addTab(wid, dettabtitle)
        lay.addWidget(dettab, 1, 0)
