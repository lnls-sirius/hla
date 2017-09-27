"""TBMagnetControlWindow module."""

import re
from siriuspy.search import MASearch
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .control_widget.BaseMagnetControlWidget import BaseMagnetControlWidget
from .control_widget.SlowCorrectorControlWidget import \
    TBSlowCorrectorControlWidget
from .detail_widget.MagnetDetailWidget import MagnetDetailWidget


class TBMagnetControlWindow(BaseMagnetControlWindow):
    """TBMagnetControlWindow class."""

    def __init__(self, parent=None):
        """Init."""
        self._magnets = [re.sub("PS-", "MA-", x) for x in
                         MASearch.get_manames([{"section": "TB"}])]
        super(TBMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('TB Magnet Control Panel')

    def _addTabs(self):
        self.tabs.setObjectName("ToBoosterTab")
        self.dipo_tab = MagnetDetailWidget("TB-Fam:MA-B", self)
        self.slow_tab = TBSlowCorrectorControlWidget(
                            self._magnets,
                            BaseMagnetControlWidget.VERTICAL,
                            parent=self)
        # Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        # Make button connections
        # self._connectButtons(self.slow_tab.findChildren(QPushButton))
