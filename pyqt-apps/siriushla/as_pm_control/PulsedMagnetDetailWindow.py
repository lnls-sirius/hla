"""Define detail window for a pulsed magnet."""
from pydm import PyDMApplication
from siriushla.widgets import SiriusMainWindow
from .PulsedMagnetDetailWidget import PulsedMagnetDetailWidget


class PulsedMagnetDetailWindow(SiriusMainWindow):
    """Window with all controls of Pulsed Manget."""

    def __init__(self, maname, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._maname = maname
        self.app = PyDMApplication.instance()
        self._setup_ui()
        # app.establish_widget_connections(self)

    def _setup_ui(self):
        self.central_widget = PulsedMagnetDetailWidget(self._maname, self)
        self.setCentralWidget(self.central_widget)
