"""Module that defines the window resposible for controlling the SR magnets."""
import re

from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow
from siriuspy.search import MASearch
from .BaseMagnetControlWindow import BaseMagnetControlWindow
from .detail_widget.DipoleDetailWidget import DipoleDetailWidget
from .control_widget.FamQuadrupoleControlWidget \
    import SiFamQuadrupoleControlWidget
from .control_widget.FamSextupoleControlWidget \
    import SiFamSextupoleControlWidget
from .control_widget.SlowCorrectorControlWidget \
    import SiSlowCorrectorControlWidget
from .control_widget.FastCorrectorControlWidget \
    import SiFastCorrectorControlWidget
from .control_widget.SkewQuadControlWidget import SiSkewQuadControlWidget


class SIMagnetControlWindow(BaseMagnetControlWindow):
    """Window to control all storage ring's magnets."""

    def __init__(self, parent=None):
        """Class constructor."""
        self._magnets = [re.sub("PS-", "MA-", x)
                         for x in MASearch.get_manames([{"section": "SI"}])]
        self._trim_windows = dict()
        super(SIMagnetControlWindow, self).__init__(parent)
        self.setWindowTitle('SI Magnet Control Panel')

    def _addTabs(self):
        self.dipo_tab = DipoleDetailWidget("SI-Fam:MA-B1B2", self)
        self.quad_tab = \
            SiFamQuadrupoleControlWidget(self._magnets, parent=self)
        self.sext_tab = SiFamSextupoleControlWidget(self._magnets, parent=self)
        self.slow_tab = \
            SiSlowCorrectorControlWidget(self._magnets, parent=self)
        self.fast_tab = \
            SiFastCorrectorControlWidget(self._magnets, parent=self)
        self.skew_tab = SiSkewQuadControlWidget(self._magnets, parent=self)
        # Add Tabs
        self.tabs.addTab(self.dipo_tab, "Dipoles")
        self.tabs.addTab(self.quad_tab, "Quadrupoles")
        self.tabs.addTab(self.sext_tab, "Sextupoles")
        self.tabs.addTab(self.slow_tab, "Slow Correctors")
        self.tabs.addTab(self.fast_tab, "Fast Correctors")
        self.tabs.addTab(self.skew_tab, "Skew Quad")
        # Make button connections
        for magnet_widget in self.quad_tab.findChildren(MagnetWidget):
            try:
                button = magnet_widget.trim_button
            except Exception:
                pass
            else:
                button.clicked.connect(self._open_trim_window)
        # self._connectButtons(self.quad_tab.findChildren(QPushButton))
        # self._connectButtons(self.sext_tab.findChildren(QPushButton))
        # self._connectButtons(self.slow_tab.findChildren(QPushButton))
        # self._connectButtons(self.fast_tab.findChildren(QPushButton))
        # self._connectButtons(self.skew_tab.findChildren(QPushButton))

    def _open_trim_window(self):
        button = self.sender()
        maname = button.parent().maname
        if maname not in self._trim_windows:
            self._trim_windows[maname] = MagnetTrimWindow(
                maname=maname, parent=self)
        self._trim_windows[maname].show()
