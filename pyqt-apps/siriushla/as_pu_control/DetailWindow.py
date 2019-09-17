"""Define detail window for a pulsed magnet."""
import qtawesome as qta
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util
from siriushla.widgets import SiriusMainWindow
from .DetailWidget import PUDetailWidget


class PUDetailWindow(SiriusMainWindow):
    """Window with all controls of Pulsed Manget."""

    def __init__(self, devname, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._section = self._devname.sec
        self._devtype = self._devname.dis
        self.setObjectName(self._section+'App')
        self.setWindowTitle(self._devname)
        self.setWindowIcon(
            qta.icon('mdi.current-ac',
                     color=util.get_appropriate_color(self._section)))
        self._setup_ui()

    def _setup_ui(self):
        self.central_widget = PUDetailWidget(self._devname, self)
        self.setCentralWidget(self.central_widget)
