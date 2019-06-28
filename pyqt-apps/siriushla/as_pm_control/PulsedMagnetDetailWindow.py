"""Define detail window for a pulsed magnet."""
from pydm import PyDMApplication
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusMainWindow
from .PulsedMagnetDetailWidget import PulsedMagnetDetailWidget


class PulsedMagnetDetailWindow(SiriusMainWindow):
    """Window with all controls of Pulsed Manget."""

    def __init__(self, maname, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._maname = _PVName(maname)
        self.setObjectName(self._maname.sec+'App')
        self.app = PyDMApplication.instance()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._maname)
        self.central_widget = PulsedMagnetDetailWidget(self._maname, self)
        self.setCentralWidget(self.central_widget)
