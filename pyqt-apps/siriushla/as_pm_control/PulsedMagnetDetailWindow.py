"""Define detail window for a pulsed magnet."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QMainWindow
from .PulsedMagnetDetailWidget import PulsedMagnetDetailWidget


class PulsedMagnetDetailWindow(QMainWindow):
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

    def showEvent(self, event):
        """Establish connections and call super."""
        self.app.establish_widget_connections(self)
        super().showEvent(event)

    def closeEvent(self, event):
        """Override closeEvent in order to close iwdget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)
