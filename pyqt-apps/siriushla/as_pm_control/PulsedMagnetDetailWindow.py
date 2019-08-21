"""Define detail window for a pulsed magnet."""
import qtawesome as qta
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
        self.setWindowTitle(self._maname)
        self.setWindowIcon(qta.icon('mdi.current-ac', color='#969696'))
        self._setup_ui()

    def _setup_ui(self):
        self.central_widget = PulsedMagnetDetailWidget(self._maname, self)
        self.setCentralWidget(self.central_widget)
